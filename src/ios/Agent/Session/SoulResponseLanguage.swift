import Foundation

/// Shared by the Soul picker, minis-config schema and system prompt.
enum SoulResponseLanguage: String, CaseIterable {
    case auto, zh, en, hr

    var displayName: String {
        switch self {
        case .auto: return "Auto"
        case .zh: return "Chinese"
        case .en: return "English"
        case .hr: return "Croatian"
        }
    }

    var instructions: String {
        guard self != .auto else { return "" }
        let language = self == .hr ? "Croatian (hr-HR, hrvatski)" : displayName
        var text = "\n\nResponse language (SOUL.md lang): Reply in \(language), even when the request or tool output is in another language, unless the user explicitly asks for another language. This preference overrides the default match-the-input language rule. Keep code, commands, paths, URLs and exact quoted data unchanged."
        if self == .hr {
            text += " Use standard Croatian and Latin script with č, ć, đ, š and ž. Odgovaraj na hrvatskom jeziku, jasno i sažeto."
        }
        return text
    }
}
