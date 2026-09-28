"""Master Content Moderation Pipeline for PCMC Sarathi AI."""

import time
from typing import Optional
from moderation.schemas import (
    CitizenInputPayload,
    ModerationCheckResponse,
    SafetyStatus,
    ViolationCategory,
    OutputModerationPayload,
    OutputModerationResponse,
)
from moderation.pii_masking.pii_masker import PIIMasker
from moderation.profanity_filter.profanity_detector import ProfanityDetector
from moderation.safety_controls.injection_detector import InjectionDetector
from moderation.safety_controls.file_validator import FileValidator
from moderation.content_moderation.output_moderator import OutputModerator
from moderation.templates.warning_messages import get_polite_warning
from shared.config.settings import settings


class ContentModerationPipeline:
    """
    Central Content Moderation Pipeline.
    Executes in-flight synchronous checks on all citizen inputs and LLM outputs.
    """

    def __init__(self):
        self.pii_masker = PIIMasker(preserve_last_digits=True)
        self.profanity_detector = ProfanityDetector(
            sensitivity=settings.moderation.profanity_sensitivity
        )
        self.injection_detector = InjectionDetector(
            threshold=settings.moderation.prompt_injection_threshold
        )
        self.file_validator = FileValidator()
        self.output_moderator = OutputModerator()

    async def moderate_input(self, payload: CitizenInputPayload) -> ModerationCheckResponse:
        """
        Processes citizen incoming message through the complete moderation chain.
        """
        start_time = time.perf_counter()
        raw_text = payload.text or ""
        lang = payload.language or "mr"
        violations = []
        masked_entities = []

        # -------------------------------------------------------------
        # 1. File & Attachment Validation
        # -------------------------------------------------------------
        if payload.media_filename or payload.media_mime_type:
            is_valid_file, file_reason = self.file_validator.validate(
                filename=payload.media_filename,
                mime_type=payload.media_mime_type,
                size_bytes=payload.media_size_bytes,
            )
            if not is_valid_file:
                violations.append(ViolationCategory.UNSAFE_FILE)
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return ModerationCheckResponse(
                    is_safe=False,
                    status=SafetyStatus.UNSAFE,
                    original_text=raw_text,
                    cleaned_text="",
                    detected_language=lang,
                    violations=violations,
                    polite_warning=get_polite_warning(ViolationCategory.UNSAFE_FILE, lang),
                    audit_log={
                        "citizen_phone": payload.citizen_phone,
                        "channel": payload.channel,
                        "latency_ms": latency_ms,
                        "reason": file_reason,
                    },
                )

        # -------------------------------------------------------------
        # 2. Prompt Injection & Jailbreak Defense
        # -------------------------------------------------------------
        if settings.moderation.enable_prompt_injection_check and raw_text:
            is_injection, matched_patterns, risk = self.injection_detector.check(raw_text)
            if is_injection:
                violations.append(ViolationCategory.PROMPT_INJECTION)
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return ModerationCheckResponse(
                    is_safe=False,
                    status=SafetyStatus.UNSAFE,
                    original_text=raw_text,
                    cleaned_text="",
                    detected_language=lang,
                    violations=violations,
                    polite_warning=get_polite_warning(ViolationCategory.PROMPT_INJECTION, lang),
                    audit_log={
                        "citizen_phone": payload.citizen_phone,
                        "channel": payload.channel,
                        "latency_ms": latency_ms,
                        "injection_patterns": matched_patterns,
                        "risk_score": risk,
                    },
                )

        # -------------------------------------------------------------
        # 3. Profanity & Abuse Filter
        # -------------------------------------------------------------
        if settings.moderation.enable_profanity_filter and raw_text:
            is_profane, matched_words, sev_score = self.profanity_detector.check(raw_text)
            if is_profane:
                violations.append(ViolationCategory.PROFANITY_ABUSE)
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return ModerationCheckResponse(
                    is_safe=False,
                    status=SafetyStatus.UNSAFE,
                    original_text=raw_text,
                    cleaned_text="",
                    detected_language=lang,
                    violations=violations,
                    polite_warning=get_polite_warning(ViolationCategory.PROFANITY_ABUSE, lang),
                    audit_log={
                        "citizen_phone": payload.citizen_phone,
                        "channel": payload.channel,
                        "latency_ms": latency_ms,
                        "profane_terms": matched_words,
                        "severity": sev_score,
                    },
                )

        # -------------------------------------------------------------
        # 4. PII Detection & Masking (DPDP Act Compliance)
        # -------------------------------------------------------------
        cleaned_text = raw_text
        if settings.moderation.enable_pii_masking and raw_text:
            cleaned_text, masked_entities = self.pii_masker.mask_text(raw_text)
            if masked_entities:
                violations.append(ViolationCategory.PII_EXPOSURE)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        status = SafetyStatus.SANITIZED_SAFE if masked_entities else SafetyStatus.SAFE

        return ModerationCheckResponse(
            is_safe=True,
            status=status,
            original_text=raw_text,
            cleaned_text=cleaned_text,
            detected_language=lang,
            violations=violations,
            masked_entities=masked_entities,
            polite_warning=None,
            audit_log={
                "citizen_phone": payload.citizen_phone,
                "channel": payload.channel,
                "latency_ms": latency_ms,
                "pii_masked_count": len(masked_entities),
            },
        )

    def moderate_output(self, payload: OutputModerationPayload) -> OutputModerationResponse:
        """
        Validates LLM output prior to citizen transmission.
        """
        return self.output_moderator.moderate_output(payload.raw_response)


# Pipeline singleton instance
moderation_pipeline = ContentModerationPipeline()
