# Ampoulex showroom update

The approved product image anchors the public homepage. The catalogue contains
1, 2, 3, 5 and 10 mL glass ampoules, each in clear and amber. One mL equals one cc.
All ten records were imported through the authenticated production product importer.
Prices and stock were not supplied; required numeric defaults are zero in admin.
The public website requests an inquiry and does not display those default prices.

## Image provenance

- Generation: built-in imagegen tool; approved by the user in this conversation.
- Website asset: `static/ampoulex-studio.webp` (58,844 bytes).
- Original copied into the local workspace at `.cache/ampoulex-studio-original.png`.
- Format conversion used Pillow; the composition and content were preserved.
- Product cards use an inline SVG macro in `templates/customer-site.html`.

### Final generation prompt

Use case: product-mockup. Create one exceptionally polished photorealistic CGI product illustration for Ampoulex glass ampoule manufacturer website. Wide 3:2 composition. Two elegant upright GLASS AMPOULES, NOT vials or bottles: slender long tubular open stems with small flared open rims, elongated pinch/neck, cylindrical lower bodies with gently rounded shoulders, flat round bases. One crystal clear glass ampoule on left and one rich honey amber glass ampoule on right, both contain NO liquid, no stopper, no cap, no label, no markings. Amber ampoule slightly taller; clear ampoule slightly forward, occupy central 60% width and 85% height. Suspended just above a subtle dark reflective circular plinth. Seamless deep charcoal almost black #0a0c0e background. Precise beautiful champagne-gold and white studio rim lights tracing the glass, realistic refraction and thickness, rich refined scientific-industrial beauty, high contrast, museum-quality still life, cinematic futuristic atmosphere. Extremely sharp edges and restrained glow. Glass shapes must clearly be pharmaceutical glass ampoules with LONG NARROW OPEN STEMS, not short neck bottles. No text, no typography, no logos, no UI, no rings in background, no blue, no red, no sparkles, no liquid. Illustration for manufacturer product showroom, not actual measured technical depiction.

## Implementation

Public template: `templates/customer-site.html`. Styles and interactions live in
`static/ampoulex-showroom.css` and `static/ampoulex-showroom.js`. Product selections
use the real database IDs and the existing `/submit-inquiry` endpoint.
The admin product form now exposes capacity and retains Clear as a colour choice.
No audio, red palette, certification claims or medication/dose descriptions are used.

## Preview observations

Desktop and 390-pixel mobile layouts were inspected in the browser. The size/colour
selector, colour filters, multi-product selection, quantity total and mobile menu
were exercised without submitting a live inquiry. Two selected products with
quantities of 2,000 and 5,000 displayed a total of 7,000 pieces. No test suite was run.
