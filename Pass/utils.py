"""Small helpers shared by the compiler: selector grammar, generator utilities."""

import functools
import re


def selector_pattern():
    """Compile and return the CSS selector grammar regex (W3C CSS2.1 grammar subset)."""
    nmstart = r'[_a-z]'
    nmchar = r'[_a-z0-9-]'
    name = nmchar + '+'
    ident = r'-?' + nmstart + nmchar + '*'
    string1 = r'\"[^\n\r\f\\"]*\"'
    string2 = r"\'[^\n\r\f\\']*\'"
    string = string1 + '|' + string2
    element_name = ident + r'|\*'
    hash = '#' + name
    class_ = r'\.' + ident
    attrib = r'\[\s*' + ident + r'\s*(?:(?:=|~=|\|=)\s*(?:' + ident + '|' + string + r')\s*)?\]'
    pseudo = r':(?:' + ident + r'|' + ident + r'\(\s*(?:' + ident + r'\s*)?\))'
    combinator = r'\+\s*|\>\s*'
    compound = r'(?:' + hash + '|' + class_ + '|' + attrib + '|' + pseudo + r')+'
    simple_selector = element_name + r'(?:' + hash + '|' + class_ + '|' + attrib + '|' + pseudo + r')*|' + compound
    selector = (simple_selector + r'(?:' + combinator + compound
                + r'|\s+(?:' + combinator + '?' + compound + r')?)?')
    return re.compile(selector)


def last(iterable, last):
    """Yield all elements of ``iterable`` followed by the ``last`` sentinel value."""
    empty = True
    for element in iterable:
        yield element
        empty = False
    if not empty:
        yield last


def is_property(line):
    """Return True if ``line`` looks like a ``property expression`` declaration."""
    if ' ' in line:
        property, _, expression = line.partition(' ')
        expression = expression.rstrip()
        if expression:
            first, tail = property[:1], property[1:]
            if first.isalpha() or first in ('_in', '-') and tail.replace('_in', 'a').replace('-', 'a').isalnum():
                return True
    return False


property_pattern = re.compile(r'^-?[_a-z][_a-z0-9-]*\s')


def is_property_(line):
    """Return a match object if ``line`` starts with a CSS property name, else None."""
    return property_pattern.match(line)


def consumer(func):
    """Decorator that primes a generator so it can be used as a push-style consumer (``send``)."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)
        return gen
    return wrapper


def memory_gen(gen):
    """Yield ``(previous, current)`` pairs of the wrapped generator."""
    @functools.wraps(gen)
    def wrapper(*args, **kwargs):
        j = None
        for i in gen(*args, **kwargs):
            if j is not None:
                yield j, i
            j = i
    return wrapper

# see http://peter.sh/experiments/vendor-prefixed-css-property-overview/
# update on that page occurred on 2013-07-20.
# Maps a property to the vendor prefixes it needs (space-separated).
vendor_prefixed_properties = {
    'accesskey': 'wap',
    'align-content': 'webkit',
    'align-items': 'webkit',
    'align-self': 'webkit',
    'animation': 'webkit',
    'animation-delay': 'webkit',
    'animation-direction': 'webkit',
    'animation-duration': 'webkit',
    'animation-fill-mode': 'webkit',
    'animation-iteration-count': 'webkit',
    'animation-name': 'webkit',
    'animation-play-state': 'webkit',
    'animation-timing-function': 'webkit',
    'app-region': 'webkit',
    'appearance': 'moz webkit',
    'aspect-ratio': 'webkit',
    'backface-visibility': 'webkit',
    'background-blend-mode': 'webkit',
    'background-clip': 'webkit',
    'background-composite': 'webkit',
    'background-inline-policy': 'moz',
    'background-origin': 'webkit',
    'background-position-x': 'ms',
    'background-position-y': 'ms',
    'background-size': 'webkit',
    'behavior': 'ms',
    'binding': 'moz',
    'blend-mode webkit': 'webkit',
    'block-progression ms': 'ms',
    'border-after webkit': 'webkit',
    'border-after-color': 'webkit',
    'border-after-style': 'webkit',
    'border-after-width': 'webkit',
    'border-before': 'webkit',
    'border-before-color': 'webkit',
    'border-before-style': 'webkit',
    'border-before-width': 'webkit',
    'border-bottom-colors': 'moz',
    'border-bottom-left-radius': 'webkit',
    'border-bottom-right-radius': 'webkit',
    'border-end': 'moz webkit',
    'border-end-color': 'moz webkit',
    'border-end-style': 'moz webkit',
    'border-end-width': 'moz webkit',
    'border-fit': 'webkit',
    'border-horizontal-spacing': 'webkit',
    'border-image': 'webkit o',
    'border-left-colors': 'moz',
    'border-radius': 'webkit',
    'border-right-colors': 'moz',
    'border-start': 'moz webkit',
    'border-start-color': 'moz webkit',
    'border-start-style': 'moz webkit',
    'border-start-width': 'moz webkit',
    'border-top-colors': 'moz',
    'border-top-left-radius': 'webkit',
    'border-top-right-radius': 'webkit',
    'border-vertical-spacing': 'webkit',
    'box-align': 'moz webkit',
    'box-decoration-break': 'webkit',
    'box-direction': 'moz webkit',
    'box-flex': 'moz webkit',
    'box-flex-group': 'webkit',
    'box-lines': 'webkit',
    'box-ordinal-group': 'moz webkit',
    'box-orient': 'moz webkit',
    'box-pack': 'moz webkit',
    'box-reflect': 'webkit',
    'box-shadow': 'webkit',
    'box-sizing': 'moz webkit',
    'caption-side': 'epub',
    'clip-path': 'webkit',
    'color-correction': 'webkit',
    'column-axis': 'webkit',
    'column-break-after': 'webkit',
    'column-break-before': 'webkit',
    'column-break-inside': 'webkit',
    'column-count': 'moz webkit',
    'column-fill': 'moz',
    'column-gap': 'moz webkit',
    'column-progression': 'webkit',
    'column-rule': 'moz webkit',
    'column-rule-color': 'moz webkit',
    'column-rule-style': 'moz webkit',
    'column-rule-width': 'moz webkit',
    'column-span': 'webkit',
    'column-width': 'moz webkit',
    'columns': 'moz webkit',
    'content-zoom-chaining': 'ms',
    'content-zoom-limit': 'ms',
    'content-zoom-limit-max': 'ms',
    'content-zoom-limit-min': 'ms',
    'content-zoom-snap': 'ms',
    'content-zoom-snap-points': 'ms',
    'content-zoom-snap-type': 'ms',
    'content-zooming': 'ms',
    'cursor-visibility': 'webkit',
    'dashboard-region': 'webkit apple',
    'device-pixel-ratio': 'o',
    'filter': 'webkit ms',
    'flex': 'webkit ms',
    'flex-align': 'ms',
    'flex-basis': 'webkit',
    'flex-direction': 'webkitms',
    'flex-flow': 'webkit',
    'flex-grow': 'webkit',
    'flex-order': 'ms',
    'flex-pack': 'ms',
    'flex-shrink': 'webkit',
    'flex-wrap': 'webkit ms',
    'float-edge': 'moz',
    'flow-from': 'webkit ms',
    'flow-into': 'webkit ms',
    'focus-opacity': 'o',
    'font-feature-settings': 'moz webkit',
    'font-kerning': 'webkit',
    'font-language-override': 'moz',
    'font-size-delta': 'webkit',
    'font-smoothing': 'webkit',
    'font-variant-ligatures': 'webkit',
    'force-broken-image-icon': 'moz',
    'grid-after': 'webkit',
    'grid-auto-columns': 'webkit',
    'grid-auto-flow': 'webkit',
    'grid-auto-rows': 'webkit',
    'grid-before': 'webkit',
    'grid-column': 'webkit ms',
    'grid-column-align': 'ms',
    'grid-column-span': 'ms',
    'grid-columns': 'ms',
    'grid-definition-columns': 'webkit',
    'grid-definition-rows': 'webkit',
    'grid-end': 'webkit',
    'grid-row': 'webkit ms',
    'grid-row-align': 'ms',
    'grid-row-span': 'ms',
    'grid-rows': 'ms',
    'grid-start': 'webkit',
    'high-contrast-adjust': 'ms',
    'highlight': 'webkit',
    'hyphenate-character': 'webkit',
    'hyphenate-limit-after': 'webkit',
    'hyphenate-limit-before': 'webkit',
    'hyphenate-limit-chars': 'ms',
    'hyphenate-limit-lines': 'webkit ms',
    'hyphenate-limit-zone': 'ms',
    'hyphens': 'moz epub ms',
    'image-region': 'moz',
    'ime-mode': 'ms',
    'input-format': 'wap',
    'input-required': 'wap',
    'interpolation-mode': 'ms',
    'interpret-as': 'xv',
    'justify-content': 'webkit',
    'layout-flow': 'ms',
    'layout-grid': 'ms',
    'layout-grid-char': 'ms',
    'layout-grid-line': 'ms',
    'layout-grid-mode': 'ms',
    'layout-grid-type': 'ms',
    'line-align': 'webkit',
    'line-box-contain': 'webkit',
    'line-break': 'webkit',
    'line-clamp': 'webkit',
    'line-grid': 'webkit',
    'line-snap': 'webkit',
    'link': 'o',
    'link-source': 'o',
    'locale': 'webkit',
    'logical-height': 'webkit',
    'logical-width': 'webkit',
    'margin-after': 'webkit',
    'margin-after-collapse': 'webkit',
    'margin-before': 'webkit',
    'margin-before-collapse': 'webkit',
    'margin-bottom-collapse': 'webkit',
    'margin-collapse': 'webkit',
    'margin-end': 'moz webkit',
    'margin-start': 'moz webkit',
    'margin-top-collapse': 'webkit',
    'marquee': 'webkit',
    'marquee-dir': 'wap',
    'marquee-direction': 'webkit',
    'marquee-increment': 'webkit',
    'marquee-loop': 'wap',
    'marquee-repetition': 'webkit',
    'marquee-speed': 'webkit wap',
    'marquee-style': 'webkit wap',
    'mask': 'webkit',
    'mask-box-image': 'webkit',
    'mask-box-image-outset': 'webkit',
    'mask-box-image-repeat': 'webkit',
    'mask-box-image-slice': 'webkit',
    'mask-box-image-source': 'webkit',
    'mask-box-image-width': 'webkit',
    'mask-clip': 'webkit',
    'mask-composite': 'webkit',
    'mask-image': 'webkit',
    'mask-origin': 'webkit',
    'mask-position': 'webkit',
    'mask-position-x': 'webkit',
    'mask-position-y': 'webkit',
    'mask-repeat': 'webkit',
    'mask-repeat-x': 'webkit',
    'mask-repeat-y': 'webkit',
    'mask-size': 'webkit',
    'max-logical-height': 'webkit',
    'max-logical-width': 'webkit',
    'min-logical-height': 'webkit',
    'min-logical-width': 'webkit',
    'mini-fold': 'o',
    'nbsp-mode': 'webkit',
    'object-fit': 'o',
    'object-position': 'o',
    'opacity': 'webkit',
    'order': 'webkit',
    'orient': 'moz',
    'outline-radius': 'moz',
    'outline-radius-bottomleft': 'moz',
    'outline-radius-bottomright': 'moz',
    'outline-radius-topleft': 'moz',
    'outline-radius-topright': 'moz',
    'overflow-scrolling': 'webkit',
    'overflow-style': 'ms',
    'overflow-x': 'ms',
    'overflow-y': 'ms',
    'padding-after': 'webkit',
    'padding-before': 'webkit',
    'padding-end': 'moz webkit',
    'padding-start': 'moz webkit',
    'perspective': 'webkit',
    'perspective-origin': 'webkit',
    'perspective-origin-x': 'webkit',
    'perspective-origin-y': 'webkit',
    'phonemes': 'xv',
    'print-color-adjust': 'webkit',
    'progress-appearance': 'ms',
    'region-break-after': 'webkit',
    'region-break-before': 'webkit',
    'region-break-inside': 'webkit',
    'region-fragment': 'webkit',
    'rtl-ordering': 'webkit',
    'ruby-position': 'webkit',
    'script-level': 'moz',
    'script-min-size': 'moz',
    'script-size-multiplier': 'moz',
    'scroll-chaining': 'ms',
    'scroll-limit': 'ms',
    'scroll-limit-x-max': 'ms',
    'scroll-limit-x-min': 'ms',
    'scroll-limit-y-max': 'ms',
    'scroll-limit-y-min': 'ms',
    'scroll-rails': 'ms',
    'scroll-snap-points-x': 'ms',
    'scroll-snap-points-y': 'ms',
    'scroll-snap-type': 'ms',
    'scroll-snap-x': 'ms',
    'scroll-snap-y': 'ms',
    'scroll-translation': 'ms',
    'scrollbar-arrow-color': 'ms',
    'scrollbar-base-color': 'ms',
    'scrollbar-darkshadow-color': 'ms',
    'scrollbar-face-color': 'ms',
    'scrollbar-highlight-color': 'ms',
    'scrollbar-shadow-color': 'ms',
    'scrollbar-track-color': 'ms',
    'shape-inside': 'webkit',
    'shape-margin': 'webkit',
    'shape-outside': 'webkit',
    'shape-padding': 'webkit',
    'stack-sizing': 'moz',
    'svg-shadow': 'webkit',
    'tab-size': 'moz o',
    'table-baseline': 'o',
    'tap-highlight-color': 'webkit',
    'text-align-last': 'moz webkit ms',
    'text-autospace': 'ms',
    'text-blink': 'moz',
    'text-combine': 'epub',
    'text-decoration-color': 'moz webkit',
    'text-decoration-line': 'moz webkit',
    'text-decoration-style': 'moz webkit',
    'text-decorations-in-effect': 'webkit',
    'text-emphasis': 'epub',
    'text-emphasis-color': 'epub',
    'text-emphasis-position': 'webkit',
    'text-emphasis-style': 'epub',
    'text-fill-color': 'webkit',
    'text-justify': 'webkit ms',
    'text-kashida-space': 'ms',
    'text-orientation': 'epub',
    'text-overflow': 'ms',
    'text-security': 'webkit',
    'text-size-adjust': 'moz',
    'text-stroke': 'webkit',
    'text-stroke-color': 'webkit',
    'text-stroke-width': 'webkit',
    'text-transform': 'epub',
    'text-underline-position': 'webkit ms',
    'touch-action': 'ms',
    'touch-callout': 'webkit',
    'transform': 'moz webkit o',
    'transform-origin': 'webkit o',
    'transform-origin-x': 'webkit',
    'transform-origin-y': 'webkit',
    'transform-origin-z': 'webkit',
    'transform-style': 'webkit',
    'transition': 'webkit o',
    'transition-delay': 'webkit o',
    'transition-duration': 'webkit o',
    'transition-property': 'webkit o',
    'transition-timing-function': 'webkit o',
    'user-drag': 'webkit',
    'user-focus': 'moz',
    'user-input': 'moz',
    'user-modify': 'moz webkit',
    'user-select': 'moz webkit ms',
    'voice-balance': 'xv',
    'voice-duration': 'xv',
    'voice-pitch': 'xv',
    'voice-pitch-range': 'xv',
    'voice-rate': 'xv',
    'voice-stress': 'xv',
    'voice-volume': 'xv',
    'window-shadow': 'moz',
    'word-break': 'epub ms',
    'word-wrap': 'ms',
    'wrap-flow': 'webkit ms',
    'wrap-through': 'ms webkit',
    'writing-mode': 'ms epub',
    'zoom': 'ms',
}