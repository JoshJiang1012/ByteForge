# ByteForge 5.0 Performance Notes

## Removed from the old rendering path
- continuously animated blurred aurora layers
- scan-beam animation
- orbiting mission rings
- constant pulsing decorative elements
- large runtime PNG character art

## 5.0 optimizations
- Performance Mode defaults to ON.
- Runtime character art is resized WebP (~40 KB main portraits; ~8 KB thumbnails).
- Syntax highlighting is scheduled with `requestAnimationFrame`.
- Draft saves use a short debounce.
- Most movement is event-triggered, not continuous.
- Heavy backdrop blur is disabled in Performance Mode.

Typing feedback is now a short non-text pulse. It does not duplicate the typed character and only runs during input.

## Character art integration performance pass

The character redesign does **not** restore the heavy 2.x animation stack. Character composition uses static WebP crops, CSS masks, gradients, and z-index layering. Patch transitions run only when its support scene opens or closes. Warden's Boss Mode is state-driven and inactive during normal missions. No character layer runs a perpetual animation loop.
