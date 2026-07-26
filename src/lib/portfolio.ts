export interface PortfolioProject {
  id: string
  title: string
  industry: string
  summary: string
  result: string
  previewImage?: string
  categories: string[]
  services: string[]
}

export const portfolioProjects: PortfolioProject[] = [
  {
    id: 'lets-smile-dental',
    title: "Let's Smile Dental",
    industry: 'Healthcare',
    summary:
      'A modern clinic website and brand system built to make booking feel simple, trustworthy, and premium.',
    result: 'Better appointment flow and a more polished local brand presence.',
    previewImage: '/websites/screenshots/lets-smile-dental.png',
    categories: ['website', 'branding', 'design'],
    services: ['Website Design', 'Brand Identity', 'Local SEO', 'GMB Setup'],
  },
  {
    id: 'tasty-bites-cafe',
    title: 'Tasty Bites Cafe',
    industry: 'Food and Beverage',
    summary:
      'A warm, image-led cafe experience designed to support discovery, menu browsing, and repeat local orders.',
    result: 'Stronger visual identity with a friendlier digital storefront.',
    previewImage: '/websites/screenshots/tasty-bites-3d-cafe.png',
    categories: ['website', 'branding', 'seo'],
    services: ['Website Design', 'Logo and Branding', 'Brochure', 'Meta Ads'],
  },
  {
    id: 'deep-water-tank-cleaning',
    title: 'Deep Water Tank Cleaning',
    industry: 'Service Business',
    summary:
      'A conversion-first service website built around trust signals, local discoverability, and direct lead capture.',
    result: 'Clearer lead funnels paired with stronger local search visibility.',
    previewImage: '/websites/screenshots/deep-water-tank-cleaning-modern.png',
    categories: ['website', 'seo', 'design'],
    services: ['Website Design', 'SEO Services', 'Google Ads', 'GMB'],
  },
  {
    id: 'mita-dental-clinic',
    title: 'Mita Dental Clinic',
    industry: 'Healthcare',
    summary:
      'A treatment-focused dental website supported by a sharper brand identity and clearer patient messaging.',
    result: 'More confidence-building content for patients across core treatments.',
    previewImage: '/websites/screenshots/mita-dental-website.png',
    categories: ['website', 'branding', 'design'],
    services: ['Website Design', 'Logo Design', 'Logo Animation', 'Infographics'],
  },
  {
    id: 'multi-specialty-dental',
    title: 'Multi-Specialty Dental Clinic',
    industry: 'Healthcare',
    summary:
      'A broad clinic site architecture for multiple services, team trust, and higher-value treatment discovery.',
    result: 'A more scalable website foundation for multi-service growth.',
    previewImage: '/websites/screenshots/dental-clinic-3d.png',
    categories: ['website', 'seo'],
    services: ['Website Design', 'SEO', 'GMB Listing', 'Hosting'],
  },
  {
    id: 'brand-identity-packages',
    title: 'Complete Brand Identity Packages',
    industry: 'Branding',
    summary:
      'Full visual identity systems for businesses that need cohesion across print, digital, and social touchpoints.',
    result: 'Consistent visual systems that make smaller brands feel established.',
    categories: ['branding', 'design'],
    services: ['Logo Design', 'Logo Animation', 'Brochure', 'Infographics'],
  },
]
