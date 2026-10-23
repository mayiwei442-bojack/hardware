//! User-facing identity for the desktop application.
//!
//! Hardware protocol names remain stable so existing keyboards and profiles
//! continue to work independently of the desktop application's branding.

pub const APP_NAME: &str = "MacroPad";
pub const APP_ID: &str = "io.macropad.desktop";

/// Runtime platform label shown beside the installed application version.
pub const PLATFORM_LABEL: &str = if cfg!(all(target_os = "macos", target_arch = "aarch64")) {
    "MAC / ARM64"
} else if cfg!(target_os = "macos") {
    "MAC / INTEL"
} else if cfg!(target_os = "windows") {
    "WIN"
} else {
    "LINUX"
};

/// Optional process-local directory for isolated previews and portable runs.
/// Empty or absent values keep the normal per-user configuration/cache paths.
pub fn data_dir_override() -> Option<std::path::PathBuf> {
    std::env::var_os("MACROPAD_DATA_DIR")
        .filter(|value| !value.is_empty())
        .map(std::path::PathBuf::from)
}

/// Release publishing is opt-in until a MacroPad manifest is deployed.
pub const UPDATE_MANIFEST_URL: &str = match option_env!("MACROPAD_UPDATE_MANIFEST_URL") {
    Some(url) => url,
    None => "",
};
