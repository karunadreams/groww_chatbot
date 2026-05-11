---
colors:
  surface: '#0e150e'
  surface-dim: '#0e150e'
  surface-bright: '#333b33'
  surface-container-lowest: '#091009'
  surface-container-low: '#161d16'
  surface-container: '#1a221a'
  surface-container-high: '#242c24'
  surface-container-highest: '#2f372e'
  on-surface: '#dce5d9'
  on-surface-variant: '#bccbb9'
  inverse-surface: '#dce5d9'
  inverse-on-surface: '#2a322a'
  outline: '#869585'
  outline-variant: '#3d4a3d'
  surface-tint: '#4ae176'
  primary: '#4be277'
  on-primary: '#003915'
  primary-container: '#22c55e'
  on-primary-container: '#004b1e'
  inverse-primary: '#006e2f'
  secondary: '#4cd7f6'
  on-secondary: '#003640'
  secondary-container: '#03b5d3'
  on-secondary-container: '#00424e'
  tertiary: '#ffb5ab'
  on-tertiary: '#60130d'
  tertiary-container: '#ff8b7c'
  on-tertiary-container: '#76231b'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6bff8f'
  primary-fixed-dim: '#4ae176'
  on-primary-fixed: '#002109'
  on-primary-fixed-variant: '#005321'
  secondary-fixed: '#acedff'
  secondary-fixed-dim: '#4cd7f6'
  on-secondary-fixed: '#001f26'
  on-secondary-fixed-variant: '#004e5c'
  tertiary-fixed: '#ffdad5'
  tertiary-fixed-dim: '#ffb4a9'
  on-tertiary-fixed: '#410001'
  on-tertiary-fixed-variant: '#7f2a21'
  background: '#0e150e'
  on-background: '#dce5d9'
  surface-variant: '#2f372e'
typography:
  display:
    fontFamily: Geist
    fontSize: 48px
    fontWeight: '600'
    lineHeight: '1.1'
    letterSpacing: -0.04em
  headline-lg:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Geist
    fontSize: 20px
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: '0'
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
    letterSpacing: '0'
  label-caps:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
  mono:
    fontFamily: Space Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: '0'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  container-max: 1440px
  gutter: 24px
  margin-desktop: 40px
  margin-mobile: 16px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style

The design system is built on a "Precision Intelligence" aesthetic. It balances the stark, high-contrast utility of developer tools with the ethereal, premium feel of high-end consumer AI. The brand personality is authoritative yet invisible, allowing the user's data and the AI's insights to take center stage.

The visual style utilizes **Glassmorphism** and **Minimalism**. Surfaces are deep and atmospheric, using layered transparency and subtle blurs to create a sense of infinite depth. High-end finishings—such as hairline strokes and radial glows—evoke a feeling of hardware-level craftsmanship. The interface should feel like a high-performance terminal viewed through a refined, modern lens.

## Colors

The palette is anchored in "Void Black" and "Deep Charcoal" to minimize ocular strain and maximize the pop of the primary accent. 

*   **Primary Accent:** Neon Green (#22C55E) is used exclusively for primary actions, success states, and active data threads.
*   **Highlight Accent:** Soft Cyan (#06B6D4) is used for secondary highlights, AI-processing indicators, and subtle data visualizations to provide a "cool" futuristic counter-balance to the green.
*   **Surface Layers:** Layers are differentiated by subtle shifts in luminosity rather than heavy color changes, moving from `#050505` (base) to `#1E1E1E` (foreground components).

## Typography

This design system employs a pairing of **Geist** for structural elements (headings, buttons, labels) and **Inter** for long-form reading and data entry. 

Spacing is intentionally generous to ensure high readability in a dark environment. For technical data or RAG-related code snippets, use a monospaced font to maintain the "developer-first" credibility. Headlines should always feature slightly negative letter spacing to feel tight and modern, while labels benefit from increased tracking for clarity at small sizes.

## Layout & Spacing

The layout follows a **Fixed Grid** model for centralized content areas (like chat interfaces or document viewers) and a **Fluid Grid** for dashboard views. 

The rhythm is based on a **4px baseline**, with standard component heights adhering to 32px, 40px, or 48px. 

**Responsive Behavior:**
- **Desktop:** 12-column grid with generous 40px outer margins.
- **Tablet:** 8-column grid with 24px margins; sidebars collapse into drawer menus.
- **Mobile:** 4-column grid with 16px margins; all cards become full-width stack elements.

## Elevation & Depth

Depth is communicated through **Tonal Layering** and **Glassmorphism**. Rather than traditional drop shadows, this design system uses:

1.  **Backdrop Blurs:** High-level floating elements (modals, dropdowns) use a `20px` saturation-boosted blur with a `0.05` opacity white tint.
2.  **Inner Glows:** Primary buttons and active cards use a very faint internal top-border glow (1px white at 10% opacity) to simulate light hitting a physical edge.
3.  **Outlines:** "Ghost Borders" are the primary method of separation. Use `1px` solid borders with low-opacity white (`rgba(255,255,255,0.08)`).
4.  **Shadows:** When necessary, use extremely large, soft ambient shadows with no spread, colored slightly toward the secondary cyan to simulate an atmospheric glow rather than a silhouette.

## Shapes

The shape language is characterized by **Smooth Rounded Corners (XL)**. This softness offsets the technical nature of the AI product, making it feel more approachable and "human-centric." 

Main containers and large cards should utilize the `radius-xl` (24px) setting. Secondary elements like input fields and buttons use `radius-md` (8px). Interactive chips and tags should remain fully rounded (pill-shaped) to distinguish them from structural components.

## Components

**Buttons:** 
- *Primary:* Neon Green background, black text. Features a `0 0 20px rgba(34, 197, 94, 0.3)` glow on hover.
- *Secondary:* Transparent with a 1px white border (15% opacity). Subtle background fill (5% white) on hover.

**Cards:**
- Deep charcoal background (#121212) with a 1px border (#1E1E1E). On hover, the border color shifts to the cyan highlight (#06B6D4) at 30% opacity.

**Input Fields:**
- Minimalist design. Only a bottom border or a very faint full border. Background should be slightly darker than the surface it sits on. Focus state triggers a neon green hairline border.

**Chips/Tags:**
- Small, uppercase Geist labels. Backgrounds should be low-opacity versions of the accent colors (e.g., Green at 10% opacity) to keep the UI clean.

**Lists:**
- High-density spacing with subtle separators. Active list items should be marked with a vertical neon green "light bar" on the left edge.

**Additional Component - AI Pulse:** 
- A custom status indicator for "RAG processing" using a breathing radial gradient transition between the primary green and secondary cyan.