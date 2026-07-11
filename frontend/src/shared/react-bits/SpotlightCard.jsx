import { useRef } from "react";

import "./SpotlightCard.css";

export default function SpotlightCard({
  as: Element = "div",
  children,
  className = "",
  spotlightColor = "rgba(23, 104, 78, 0.14)",
  ...props
}) {
  const ref = useRef(null);

  function handleMouseMove(event) {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    ref.current.style.setProperty("--mouse-x", `${event.clientX - rect.left}px`);
    ref.current.style.setProperty("--mouse-y", `${event.clientY - rect.top}px`);
    ref.current.style.setProperty("--spotlight-color", spotlightColor);
  }

  return (
    <Element
      className={`reactbits-spotlight-card ${className}`.trim()}
      onMouseMove={handleMouseMove}
      ref={ref}
      {...props}
    >
      {children}
    </Element>
  );
}
