# Cinematic Sites

## Step 1:

## Step 2: Scene Generation

### Extract Frames

## Step 3: Website Build

### Architecture Rules

- **One file** - all CSS in `<style>`, all JS in `<script>`
- **Assets external** - video and frames by relative path
- **No build step** - no React, Vue, npm, Tailwind
- **CDN only** - Google Fonts, GSAP + ScrollTriggle, Lucide Icons

### Require CDN

```html
<link
  href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap"
  rel="stylesheet"
/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://unpkg.com/lucide@latest"></script>
```

### Design System Foundation

Every site uses this CSS variable structure. Map brand colors to it:

```css
:root {
  --bg: [from brand];
  --card: [slightly off from bg];
  --text: [high contrast against bg];
  --muted: [for captions only, NOT body text]: --accent: [brand primary];
  --accent-light: [accent at 8% opacity];
  --border: [subtle divider];
}
```

### Standard Easing

The entire cinematic modules library uses one easing curve for interactive transitions. Use it everywhere:

```css
transitions: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
```

### Site Structure

```
1. HERO - Scroll-driven canvas (300vh, sticky inner, JPEG frame sequence via gsap.to + snap)
2. CINEMATIC MODULES - 2.4 modules from the library woven into content sections
3. SERVICES / FEATURES - Business copy
4. ABOUT / STORY - Business copy
5. CONTACT / CTA - Phone, email, address
6. FOOTER - Minimal
```

### Quality Standards

- Footer branding bar (fixed bottom, blurred bg, company attribution)

---

## Cinematic Modules Integration

### Source

The Cinematic Modules library lives at `http://localhost:3457/`. It contains 30+ standalone HTML modules organized into 4 categories.

### How to Use Modules

1. **Pick 2-4 modules** that match the brand's industry and vibe
2. **Fetch the module HTML**: `curl -sL http://localhost:3457/{module-name}` (no .html extension - it redirects)
3. **Read the CSS and JS** from the fetched HTML
4. **Adapt** the styles and scripts into the site, remapping colors to the brand's `--accent`, `--bg`, etc.

### Module Selection Guided by Industry

| Industry                               | Recommended Modules                                                     |
| -------------------------------------- | ----------------------------------------------------------------------- |
| Luxury (jewelry, watches, perfume)     | Text Mask Reveal, Curtain Reveal, Spotlight Border Cards, Zoom Parallax |
| Food (pizza, bakery, sushi, chocolate) | Color Shift, Zoom Parallax, Kinetic Marquee,                            |
