"""Courteous, citizen-friendly warning templates for blocked content."""

from typing import Dict
from moderation.schemas import ViolationCategory

# -------------------------------------------------------------------------
# Multilingual Polite Warning Templates (Marathi, Hindi, English)
# -------------------------------------------------------------------------

WARNING_TEMPLATES: Dict[str, Dict[ViolationCategory, str]] = {
    "mr": {
        ViolationCategory.PROFANITY_ABUSE: (
            "🙏 **नमस्कार.**\n"
            "आपल्या संदेशामध्ये आक्षेपार्ह किंवा अनुचित शब्द आढळले आहेत. "
            "पिंपरी चिंचवड महानगरपालिकेच्या नियमांनुसार कृपया सभ्य भाषेत विचारणा करावी, "
            "जेणेकरून आम्ही आपली योग्य मदत करू शकू."
        ),
        ViolationCategory.HATE_SPEECH: (
            "🙏 **नमस्कार.**\n"
            "आपल्या संदेशातील भाषा नियमांचे उल्लंघन करणारी आहे. "
            "कृपया नागरी सेवांशी संबंधित विषयांवरच आदरपूर्वक संवाद साधावा."
        ),
        ViolationCategory.PROMPT_INJECTION: (
            "🙏 **नमस्कार.**\n"
            "मी **Sarathi AI** — पिंपरी चिंचवड महानगरपालिकेचा अधिकृत नागरिक सहाय्यक आहे. "
            "मी केवळ महापालिका सेवा, कर, योजना व तक्रार निवारणाशी संबंधित प्रश्नांची उत्तरे देतो. "
            "कृपया नागरी सेवेबद्दल विचारावे."
        ),
        ViolationCategory.JAILBREAK_ATTEMPT: (
            "🙏 **नमस्कार.**\n"
            "हा प्रश्न महापालिकेच्या सुरक्षा नियमांमध्ये बसत नाही. "
            "कृपया पालिकेच्या अधिकृत सेवांबद्दल विचारणा करावी."
        ),
        ViolationCategory.UNSAFE_FILE: (
            "⚠️ **अवैध फाईल फॉरमॅट.**\n"
            "आपण अपलोड केलेली फाईल स्वीकारली जाऊ शकत नाही. "
            "कृपया केवळ PDF, JPEG, PNG किंवा ऑडिओ फाईल (कमाल मर्यादा १५ MB) अपलोड करावी."
        ),
        ViolationCategory.SPAM_FLOODING: (
            "⚠️ **वारंवार संदेश पाठवणे थांबवा.**\n"
            "एकाच वेळी खूप जलद संदेश आल्यामुळे काही सेकंद थांबावे आणि पुन्हा प्रयत्न करावा."
        ),
    },
    "hi": {
        ViolationCategory.PROFANITY_ABUSE: (
            "🙏 **नमस्ते.**\n"
            "आपके संदेश में आपत्तिजनक या अनुचित भाषा पाई गई है। "
            "कृपया पिंपरी चिंचवड नगर निगम के नियमों का पालन करते हुए शालीन भाषा में सवाल पूछें।"
        ),
        ViolationCategory.HATE_SPEECH: (
            "🙏 **नमस्ते.**\n"
            "कृपया केवल नागरिक सेवाओं और निगम योजनाओं से जुड़े सवाल ही पूछें।"
        ),
        ViolationCategory.PROMPT_INJECTION: (
            "🙏 **नमस्ते.**\n"
            "मैं **Sarathi AI** — पिंपरी चिंचवड नगर निगम का डिजिटल सहायक हूँ। "
            "कृपया नगर निगम सेवाओं, टैक्स या शिकायतों से संबंधित सवाल पूछें।"
        ),
        ViolationCategory.JAILBREAK_ATTEMPT: (
            "🙏 **नमस्ते.**\n"
            "यह अनुरोध सुरक्षा नियमों के विरुद्ध है। कृपया मान्य नगर निगम सेवाओं के बारे में पूछें।"
        ),
        ViolationCategory.UNSAFE_FILE: (
            "⚠️ **अमान्य फ़ाइल.**\n"
            "कृपया केवल PDF, JPEG, PNG या ऑडियो फ़ाइल (अधिकतम 15 MB) ही भेजें।"
        ),
        ViolationCategory.SPAM_FLOODING: (
            "⚠️ **कृपया कुछ समय प्रतीक्षा करें.**\n"
            "बार-बार संदेश भेजने के कारण थोड़ी देर बाद पुनः प्रयास करें।"
        ),
    },
    "en": {
        ViolationCategory.PROFANITY_ABUSE: (
            "🙏 **Greetings from PCMC.**\n"
            "Your message contains language that violates our civic engagement guidelines. "
            "Please rephrase your query respectfully so we can assist you with municipal services."
        ),
        ViolationCategory.HATE_SPEECH: (
            "🙏 **Greetings from PCMC.**\n"
            "Your message contains restricted content. Please keep queries focused on PCMC civic services."
        ),
        ViolationCategory.PROMPT_INJECTION: (
            "🙏 **Greetings.**\n"
            "I am **Sarathi AI**, the official virtual assistant for Pimpri Chinchwad Municipal Corporation. "
            "I can only assist with municipal services, property tax, water bills, and civic grievances."
        ),
        ViolationCategory.JAILBREAK_ATTEMPT: (
            "🙏 **Notice.**\n"
            "This request cannot be processed under municipal AI safety policies."
        ),
        ViolationCategory.UNSAFE_FILE: (
            "⚠️ **Unsupported File.**\n"
            "The uploaded file is not supported or exceeds the 15MB limit. Please upload PDF, JPEG, PNG, or Audio."
        ),
        ViolationCategory.SPAM_FLOODING: (
            "⚠️ **Too many requests.**\n"
            "Please wait a moment before sending another message."
        ),
    },
}


def get_polite_warning(violation: ViolationCategory, language: str = "mr") -> str:
    """Returns the courteous warning in the requested language (defaults to Marathi)."""
    lang_key = language.lower() if language.lower() in ("mr", "hi", "en") else "mr"
    templates_for_lang = WARNING_TEMPLATES.get(lang_key, WARNING_TEMPLATES["mr"])

    default_warning = (
        "🙏 आपल्या संदेशावर प्रक्रिया करता आली नाही. कृपया नागरी नियमांनुसार पुन्हा विचारणा करावी."
        if lang_key == "mr"
        else "🙏 Your request could not be processed under PCMC guidelines."
    )

    return templates_for_lang.get(violation, default_warning)
