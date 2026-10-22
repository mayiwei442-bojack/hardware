//! Stateless MacroPad controls for the GPUI frontend.
//!
//! These helpers only describe appearance. Callers remain responsible for
//! focus, keyboard handling, enabled-state policy, and application state.
//! Long-form and user-authored text intentionally inherits the system UI font;
//! Monaco is used only for short control legends and uppercase status labels.

use crate::pixel::{
    self, accent_color, accent_highlight_color, accent_soft_color, border_color, danger_color,
    dim_text_color, focus_color, key_color, muted_text_color, on_accent_color, panel_color,
    raised_color, shadow_color, success_color, success_soft_color, text_color, BadgeTone,
};
use gpui::prelude::{FluentBuilder, InteractiveElement};
use gpui::{
    div, point, px, AnyElement, App, BoxShadow, ClickEvent, Div, ElementId, Hsla, IntoElement,
    ParentElement, SharedString, StatefulInteractiveElement, Styled, Window,
};
use gpui_component::StyledExt;

const MONO_FONT: &str = pixel::mono_font();
const SYSTEM_FONT: &str = pixel::ui_font();

fn hard_shadow(offset: f32) -> Vec<BoxShadow> {
    vec![BoxShadow {
        color: shadow_color(),
        offset: point(px(offset), px(offset)),
        blur_radius: px(0.),
        spread_radius: px(0.),
    }]
}

fn tone_color(tone: BadgeTone) -> Hsla {
    match tone {
        BadgeTone::Neutral => muted_text_color(),
        BadgeTone::Accent | BadgeTone::Warning => accent_color(),
        BadgeTone::Success => success_color(),
        BadgeTone::Danger => danger_color(),
        BadgeTone::Info => focus_color(),
    }
}

/// Presentation flags for a keycap-like device cell.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct CellVisual {
    pub selected: bool,
    pub live: bool,
    pub warning: bool,
}

/// A keycap-like cell used for physical controls or device slots.
///
/// `icon` is a pre-rendered catalog-aware visual. This keeps Lucide font
/// glyphs and Simple Icons SVGs behind one presentation boundary.
pub fn keycap_device_cell(
    label: impl Into<SharedString>,
    icon: Option<AnyElement>,
    detail: impl Into<SharedString>,
    visual: CellVisual,
    cell: usize,
) -> Div {
    let label = label.into();
    let _detail: SharedString = detail.into();
    let colored_key = cell < 2;
    let face = match cell {
        0 => accent_color(),
        1 => pixel::secondary_color(),
        13..=15 => pixel::deck_color(),
        _ if visual.live => success_soft_color(),
        _ if visual.selected => accent_soft_color(),
        _ => key_color(),
    };
    let foreground = if cell == 1 {
        pixel::plate_ink_color()
    } else if colored_key {
        on_accent_color()
    } else {
        text_color()
    };
    let outline = if visual.warning {
        danger_color()
    } else if visual.selected || visual.live {
        accent_color()
    } else {
        border_color()
    };
    let legend = match cell {
        13 => "ENC".to_string(),
        14 => "X / Y".to_string(),
        15 => "TOUCH".to_string(),
        _ => format!("{:02}", cell + 1),
    };
    let glyph = icon.unwrap_or_else(|| {
        div()
            .font_family(pixel::mono_font())
            .text_size(px(22.))
            .child(match cell {
                13 => "+".to_string(),
                14 => "+".to_string(),
                15 => "·".to_string(),
                _ => format!("{:02}", cell + 1),
            })
            .into_any_element()
    });
    let control = div().flex().items_center().justify_center().child(glyph);
    let control = match cell {
        13 => control
            .size(px(42.))
            .rounded(px(24.))
            .bg(gpui::rgb(0xc4cac5))
            .text_color(pixel::plate_ink_color())
            .border_2()
            .border_color(gpui::rgb(0x7e8a7f))
            .into_any_element(),
        14 => control
            .size(px(40.))
            .rounded(px(24.))
            .bg(pixel::secondary_color())
            .text_color(pixel::plate_ink_color())
            .border_2()
            .border_color(gpui::rgb(0xb9a3ff))
            .into_any_element(),
        15 => control
            .size(px(38.))
            .rounded(px(22.))
            .border_2()
            .border_color(pixel::secondary_color())
            .text_color(accent_color())
            .into_any_element(),
        _ => control
            .size(px(32.))
            .text_color(foreground)
            .into_any_element(),
    };
    div()
        .w(px(96.))
        .h(px(96.))
        .flex_none()
        .p(px(7.))
        .flex()
        .flex_col()
        .gap(px(3.))
        .bg(face)
        .border_1()
        .border_color(outline)
        .rounded(px(1.))
        .shadow(hard_shadow(3.))
        .overflow_hidden()
        .font_family(pixel::ui_font())
        .text_color(foreground)
        .child(
            div()
                .w_full()
                .flex()
                .items_center()
                .justify_between()
                .font_family(pixel::mono_font())
                .text_size(px(8.))
                .child(legend)
                .child(div().size(px(4.)).bg(if visual.live || visual.selected {
                    foreground
                } else {
                    face
                })),
        )
        .child(
            div()
                .flex_1()
                .flex()
                .items_center()
                .justify_center()
                .child(control),
        )
        .child(
            div()
                .w_full()
                .truncate()
                .text_center()
                .text_size(px(10.))
                .font_semibold()
                .child(label),
        )
        .when(visual.selected, |el| {
            el.border_2().border_color(if cell == 0 {
                pixel::plate_ink_color()
            } else {
                accent_color()
            })
        })
        .hover(move |el| {
            el.border_color(if colored_key {
                text_color()
            } else {
                accent_color()
            })
        })
}

/// A compact label/value pair for read-only inspector fields.
pub fn field_readout(label: impl Into<SharedString>, value: impl Into<SharedString>) -> Div {
    div()
        .w_full()
        .flex()
        .flex_col()
        .gap(px(4.))
        .font_family(SYSTEM_FONT)
        .child(
            div()
                .text_size(px(11.))
                .font_family(MONO_FONT)
                .font_semibold()
                .text_color(dim_text_color())
                .child(label.into()),
        )
        .child(
            div()
                .min_h(px(34.))
                .flex()
                .items_center()
                .text_size(px(13.))
                .text_color(text_color())
                .child(value.into()),
        )
}

fn cycle_arrow(symbol: &'static str) -> Div {
    div()
        .w(px(36.))
        .h_full()
        .flex()
        .items_center()
        .justify_center()
        .text_size(px(14.))
        .font_family(MONO_FONT)
        .font_semibold()
        .text_color(muted_text_color())
        .cursor_pointer()
        .hover(|style| {
            style
                .bg(accent_soft_color())
                .text_color(accent_highlight_color())
        })
        .child(symbol)
}

/// A previous/value/next cycle control.
///
/// The two arrow faces receive independent element IDs and click handlers so
/// callers can address them directly for focus, tests, and event routing.
pub fn cycle_control(
    value: impl Into<SharedString>,
    previous_id: ElementId,
    next_id: ElementId,
    on_previous: impl Fn(&ClickEvent, &mut Window, &mut App) + 'static,
    on_next: impl Fn(&ClickEvent, &mut Window, &mut App) + 'static,
) -> Div {
    div()
        .w_full()
        .h(px(36.))
        .flex()
        .items_center()
        .bg(raised_color())
        .rounded(px(2.))
        .overflow_hidden()
        .font_family(SYSTEM_FONT)
        .child(cycle_arrow("<").id(previous_id).on_click(on_previous))
        .child(
            div()
                .h_full()
                .flex_1()
                .px(px(10.))
                .flex()
                .items_center()
                .justify_center()
                .text_size(px(13.))
                .text_color(text_color())
                .child(value.into()),
        )
        .child(cycle_arrow(">").id(next_id).on_click(on_next))
}

/// A switch face. Attach the control ID and listener to the returned `Div`.
pub fn toggle_face(label: impl Into<SharedString>, active: bool, enabled: bool) -> Div {
    let foreground = if !enabled {
        dim_text_color()
    } else {
        text_color()
    };

    let toggle = div()
        .h(px(34.))
        .flex()
        .items_center()
        .gap(px(10.))
        .font_family(SYSTEM_FONT)
        .text_color(foreground)
        .child(
            div()
                .flex_1()
                .text_size(px(13.))
                .font_semibold()
                .child(label.into()),
        )
        .child(
            div()
                .w(px(36.))
                .h(px(18.))
                .p(px(2.))
                .flex()
                .items_center()
                .bg(if active {
                    accent_color()
                } else {
                    raised_color()
                })
                .rounded(px(2.))
                .child(if active { div().flex_1() } else { div() })
                .child(div().w(px(12.)).h(px(12.)).bg(if enabled {
                    if active {
                        on_accent_color()
                    } else {
                        muted_text_color()
                    }
                } else {
                    dim_text_color()
                }))
                .child(if active { div() } else { div().flex_1() }),
        );

    if enabled {
        toggle.cursor_pointer()
    } else {
        toggle
    }
}

/// The outer hardware-style frame for a modal or blocking sheet.
///
/// Add a [`modal_header`] and modal content as children at the call site.
pub fn modal_frame() -> Div {
    div()
        .w(px(560.))
        .flex()
        .flex_col()
        .bg(panel_color())
        .rounded(px(1.))
        .shadow(hard_shadow(4.))
        .font_family(SYSTEM_FONT)
        .text_color(text_color())
}

/// A modal title strip with an optional explanatory subtitle.
pub fn modal_header(title: impl Into<SharedString>, subtitle: Option<SharedString>) -> Div {
    let content = div().flex_1().flex().flex_col().gap(px(4.)).child(
        div()
            .text_size(px(18.))
            .font_semibold()
            .text_color(text_color())
            .child(title.into()),
    );
    let content = if let Some(subtitle) = subtitle {
        content.child(
            div()
                .text_size(px(13.))
                .text_color(muted_text_color())
                .child(subtitle),
        )
    } else {
        content
    };

    div()
        .w_full()
        .p(px(18.))
        .flex()
        .items_center()
        .font_family(SYSTEM_FONT)
        .child(content)
}

/// A bordered status row with a semantic color rail.
pub fn status_rail(
    label: impl Into<SharedString>,
    detail: impl Into<SharedString>,
    tone: BadgeTone,
) -> Div {
    let color = tone_color(tone);
    div()
        .w_full()
        .min_h(px(34.))
        .flex()
        .items_center()
        .gap(px(8.))
        .font_family(SYSTEM_FONT)
        .child(div().w(px(5.)).h(px(5.)).flex_none().bg(color))
        .child(
            div()
                .flex_1()
                .min_w(px(0.))
                .flex()
                .items_center()
                .gap(px(8.))
                .child(
                    div()
                        .flex_none()
                        .text_size(px(10.))
                        .font_family(MONO_FONT)
                        .font_semibold()
                        .text_color(color)
                        .child(label.into()),
                )
                .child(
                    div()
                        .flex_1()
                        .min_w(px(0.))
                        .text_size(px(12.))
                        .text_color(muted_text_color())
                        .child(detail.into()),
                ),
        )
}

/// A single diagnostic or activity-log line.
pub fn log_line(
    label: impl Into<SharedString>,
    message: impl Into<SharedString>,
    tone: BadgeTone,
) -> Div {
    let color = tone_color(tone);
    div()
        .w_full()
        .min_h(px(30.))
        .px(px(8.))
        .flex()
        .items_center()
        .gap(px(8.))
        .font_family(SYSTEM_FONT)
        .child(div().w(px(4.)).h(px(4.)).bg(color))
        .child(
            div()
                .w(px(72.))
                .text_size(px(10.))
                .font_family(MONO_FONT)
                .font_semibold()
                .text_color(color)
                .child(label.into()),
        )
        .child(
            div()
                .flex_1()
                .text_size(px(13.))
                .text_color(text_color())
                .child(message.into()),
        )
}

/// A compact keyboard-modifier chip such as `CMD`, `CTRL`, or `SHIFT`.
pub fn modifier_chip(label: impl Into<SharedString>, active: bool) -> Div {
    div()
        .h(px(24.))
        .px(px(7.))
        .flex()
        .items_center()
        .justify_center()
        .bg(if active {
            accent_color()
        } else {
            raised_color()
        })
        .rounded(px(2.))
        .text_size(px(10.))
        .font_family(MONO_FONT)
        .font_semibold()
        .text_color(if active {
            on_accent_color()
        } else {
            muted_text_color()
        })
        .child(label.into())
}

/// A quiet empty-state panel for unselected or unavailable content.
pub fn empty_hint(title: impl Into<SharedString>, body: impl Into<SharedString>) -> Div {
    div()
        .w_full()
        .p(px(24.))
        .flex()
        .flex_col()
        .items_center()
        .gap(px(8.))
        .font_family(SYSTEM_FONT)
        .child(
            div()
                .text_size(px(15.))
                .font_semibold()
                .text_color(text_color())
                .child(title.into()),
        )
        .child(
            div()
                .text_size(px(13.))
                .text_color(muted_text_color())
                .child(body.into()),
        )
}

/// Re-export the shared panel primitive for callers that want a matching body.
pub fn panel_body() -> Div {
    pixel::panel().font_family(SYSTEM_FONT)
}
