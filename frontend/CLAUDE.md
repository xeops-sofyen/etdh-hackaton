# Drone Mission Control - Frontend Styling Guidelines

## Design Philosophy

This application uses a **dark military control center aesthetic** inspired by tactical command interfaces. The design emphasizes:

- High contrast for readability in mission-critical scenarios
- Terminal/monospace typography for technical data
- Glowing green accents suggesting active systems
- Minimal but impactful animations
- Clean, functional layouts without unnecessary decoration

---

## Color Palette

### Base Colors

```css
/* Backgrounds - Deep blacks and dark grays */
--bg-primary: #0a0e14;        /* Main background */
--bg-secondary: #111827;      /* Secondary surfaces */
--bg-tertiary: #1f2937;       /* Elevated surfaces */
--bg-elevated: #374151;       /* Hover/active states */

/* Borders */
--border-primary: #1f2937;    /* Subtle borders */
--border-secondary: #374151;  /* More prominent borders */
--border-tertiary: #4b5563;   /* Hover borders */
```

### Accent Colors

```css
/* Primary - Military Green (for active systems, success) */
--green-dark: #059669;
--green-primary: #10b981;
--green-light: #34d399;
--green-lighter: #6ee7b7;

/* Secondary - Blue (for informational states) */
--blue-primary: #3b82f6;
--blue-light: #93c5fd;

/* Danger - Red (for warnings, errors, abort) */
--red-dark: #dc2626;
--red-primary: #ef4444;
--red-light: #f87171;

/* Neutral Text */
--text-primary: #e5e7eb;      /* Main text */
--text-secondary: #9ca3af;    /* Secondary text */
--text-tertiary: #6b7280;     /* Muted text */
--text-disabled: #4b5563;     /* Disabled text */
```

### Usage Guidelines

- **Green**: Primary actions, active missions, success states, telemetry data
- **Blue**: Planned missions, informational messages, instructions
- **Red**: Danger actions (abort, delete), failed missions, errors
- **Gray**: Completed/past missions, neutral actions

---

## Typography

### Font Families

```css
/* Primary - Monospace (for data, labels, buttons) */
font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;

/* Secondary - System (for body text, descriptions) */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
```

### Type Scale

```css
/* Labels and metadata */
--text-xs: 10px;       /* Use with uppercase, letter-spacing: 0.5px */
--text-sm: 11px;       /* Use with uppercase, letter-spacing: 0.5px */
--text-base: 12px;     /* Standard button/label size */
--text-md: 13px;       /* Input fields, body text */

/* Headings */
--text-lg: 14px;       /* Section headers */
--text-xl: 16px;       /* Page titles */
--text-2xl: 18px;      /* Modal titles */

/* Data Display */
--text-data: 24px;     /* Telemetry values, large numbers */
```

### Typography Patterns

**Labels (uppercase, monospace)**
```css
font-size: 10px;
font-weight: 700;
text-transform: uppercase;
letter-spacing: 1px;
font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
color: var(--text-tertiary);
```

**Data Values (monospace, green glow)**
```css
font-size: 24px;
font-weight: 700;
color: #10b981;
font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
text-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
```

**Button Text (uppercase, monospace, bold)**
```css
font-size: 12px;
font-weight: 700;
text-transform: uppercase;
letter-spacing: 0.5px;
font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
```

---

## Component Patterns

### Buttons

**Primary Action (Green)**
```css
background: linear-gradient(135deg, #10b981 0%, #059669 100%);
color: #0a0e14;
border: 1px solid #34d399;
border-radius: 4px;
padding: 10px 20px;
box-shadow: 0 0 10px rgba(16, 185, 129, 0.3);

/* Hover */
background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
box-shadow: 0 0 15px rgba(16, 185, 129, 0.5);
transform: translateY(-1px);
```

**Danger Action (Red)**
```css
background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
color: #fff;
border: 1px solid #f87171;
box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);

/* Hover */
background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
box-shadow: 0 0 15px rgba(239, 68, 68, 0.5);
transform: translateY(-1px);
```

**Secondary Action (Gray)**
```css
background: #374151;
color: #e5e7eb;
border: 1px solid #4b5563;

/* Hover */
background: #4b5563;
border-color: #6b7280;
```

**Disabled State**
```css
background: #374151;
border-color: #4b5563;
color: #6b7280;
cursor: not-allowed;
box-shadow: none;
```

### Cards

**Standard Card with Accent Bar**
```css
background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
border: 1px solid #374151;
border-radius: 4px;
position: relative;

/* Left accent bar */
&::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: #10b981;
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
}

/* Hover */
background: linear-gradient(135deg, #374151 0%, #1f2937 100%);
border-color: #4b5563;
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
```

**Selected Card**
```css
border-color: #10b981;
background: linear-gradient(135deg, #1f2937 0%, #0f1419 100%);
box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
```

### Input Fields

```css
background: #1f2937;
color: #e5e7eb;
border: 1px solid #374151;
border-radius: 4px;
padding: 10px 14px;
font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
transition: all 0.2s;

/* Focus */
border-color: #10b981;
background: #111827;
box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
outline: none;
```

### Status Badges

**Active**
```css
background: rgba(16, 185, 129, 0.2);
color: #10b981;
border: 1px solid #10b981;
box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
```

**Planned**
```css
background: rgba(59, 130, 246, 0.2);
color: #3b82f6;
border: 1px solid #3b82f6;
```

**Failed**
```css
background: rgba(239, 68, 68, 0.2);
color: #ef4444;
border: 1px solid #ef4444;
box-shadow: 0 0 10px rgba(239, 68, 68, 0.2);
```

**Completed**
```css
background: rgba(107, 114, 128, 0.2);
color: #9ca3af;
border: 1px solid #6b7280;
```

---

## Visual Effects

### Glowing Effects

Use sparingly for emphasis on active/interactive elements:

```css
/* Green glow (primary actions, active states) */
box-shadow: 0 0 10px rgba(16, 185, 129, 0.3);

/* Stronger glow on hover */
box-shadow: 0 0 15px rgba(16, 185, 129, 0.5);

/* Red glow (danger states) */
box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
```

### Gradients

Use for depth and visual hierarchy:

```css
/* Dark surface gradient */
background: linear-gradient(135deg, #1f2937 0%, #111827 100%);

/* Vertical gradient for sidebars */
background: linear-gradient(180deg, #0f1419 0%, #0a0e14 100%);

/* Button gradient */
background: linear-gradient(135deg, #10b981 0%, #059669 100%);
```

### Transitions

Keep transitions subtle and fast:

```css
transition: all 0.2s ease;  /* Standard for most interactions */
transition: background 0.2s; /* For background-only changes */
```

### Hover States

```css
/* Lift effect for buttons */
transform: translateY(-1px);

/* Enhanced glow */
box-shadow: 0 0 15px rgba(16, 185, 129, 0.5);
```

---

## Layout & Spacing

### Spacing Scale

```css
--space-xs: 4px;
--space-sm: 8px;
--space-md: 12px;
--space-lg: 16px;
--space-xl: 20px;
--space-2xl: 24px;
--space-3xl: 32px;
```

### Common Patterns

**Panel Padding**
```css
padding: 20px 24px;  /* Horizontal sections */
padding: 24px;       /* Uniform padding */
```

**Gap Between Elements**
```css
gap: 12px;  /* Buttons, form controls */
gap: 16px;  /* List items */
gap: 24px;  /* Section spacing */
```

**Border Radius**
```css
border-radius: 4px;   /* Standard for all components */
border-radius: 8px;   /* Larger modals */
border-radius: 2px;   /* Accent bars, small details */
```

---

## Scrollbars

Custom dark scrollbars for consistency:

```css
.container::-webkit-scrollbar {
  width: 8px;
}

.container::-webkit-scrollbar-track {
  background: #111827;
}

.container::-webkit-scrollbar-thumb {
  background: #374151;
  border-radius: 4px;
}

.container::-webkit-scrollbar-thumb:hover {
  background: #4b5563;
}
```

---

## Map Integration

Maps should be slightly darkened to blend with the UI:

```css
.leafletContainer {
  filter: brightness(0.85) contrast(1.1);
}
```

---

## Animations

### Modal Entrance

```css
@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal {
  animation: slideUp 0.3s ease-out;
}
```

### Overlay Fade

```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.overlay {
  animation: fadeIn 0.2s ease-out;
}
```

### Loading States

```css
@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.typing span {
  background: #10b981;
  animation: bounce 1.4s infinite ease-in-out;
  box-shadow: 0 0 4px rgba(16, 185, 129, 0.5);
}
```

---

## Best Practices

### DO ✅

- Use monospace fonts for data, labels, and buttons
- Apply uppercase + letter-spacing to labels
- Use green for primary actions and active states
- Add subtle glows to interactive elements
- Keep gradients dark and subtle
- Use 4px border radius consistently
- Include hover states with slight transforms
- Apply left accent bars to cards
- Use box-shadows for depth, not borders alone

### DON'T ❌

- Mix light and dark themes
- Use bright, saturated colors outside the accent palette
- Overuse animations (keep subtle)
- Use large border radius (>8px)
- Forget focus states on interactive elements
- Use white backgrounds
- Mix sans-serif with monospace inconsistently
- Add unnecessary decoration

---

## Accessibility Notes

- **High Contrast**: Green (#10b981) on dark backgrounds meets WCAG AA
- **Focus Indicators**: All interactive elements have visible focus states
- **Color + Text**: Status is indicated by both color AND text labels
- **Monospace Fonts**: Ensure fallbacks are available for all systems

---

## Examples

### Creating a New Button

```tsx
<button className={styles.primaryButton}>
  Deploy Mission
</button>
```

```css
.primaryButton {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #0a0e14;
  border: 1px solid #34d399;
  border-radius: 4px;
  padding: 10px 20px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
  cursor: pointer;
  transition: all 0.2s;
}

.primaryButton:hover {
  background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
  box-shadow: 0 0 15px rgba(16, 185, 129, 0.5);
  transform: translateY(-1px);
}
```

### Creating a Data Panel

```tsx
<div className={styles.telemetryPanel}>
  <div className={styles.telemetryItem}>
    <span className={styles.telemetryLabel}>Battery</span>
    <span className={styles.telemetryValue}>87%</span>
  </div>
</div>
```

```css
.telemetryPanel {
  padding: 20px;
  background: linear-gradient(135deg, #0f1419 0%, #111827 100%);
  border-top: 1px solid #374151;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 24px;
}

.telemetryItem {
  padding: 12px;
  background: rgba(16, 185, 129, 0.05);
  border-left: 2px solid #10b981;
  border-radius: 2px;
}

.telemetryLabel {
  font-size: 10px;
  color: #6b7280;
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 1px;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
}

.telemetryValue {
  font-size: 24px;
  font-weight: 700;
  color: #10b981;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
  text-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
}
```

---

## Quick Reference

| Element | Background | Text Color | Border | Special |
|---------|-----------|------------|--------|---------|
| Primary Button | Green gradient | Dark | Green | Glow effect |
| Danger Button | Red gradient | White | Red | Glow effect |
| Input (default) | #1f2937 | #e5e7eb | #374151 | - |
| Input (focus) | #111827 | #e5e7eb | #10b981 | Green glow |
| Card | Dark gradient | #e5e7eb | #374151 | Left accent bar |
| Label | Transparent | #6b7280 | - | Uppercase, monospace |
| Data Value | Transparent | #10b981 | - | Monospace, glow |
| Modal | Dark gradient | #e5e7eb | #374151 | Slide-up animation |

---

**Remember**: This is a tactical interface. Every design decision should serve clarity, efficiency, and the mission-critical nature of drone operations.
