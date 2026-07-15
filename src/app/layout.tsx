import type { Metadata } from "next";
import { Inter, Poppins } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import ScrollToTop from "@/components/ScrollToTop";
import WhatsAppFloat from "@/components/WhatsAppFloat";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800", "900"],
  display: "swap",
  variable: "--font-poppins",
});

export const metadata: Metadata = {
  title: {
    default: "TKVibes - Full-Service Digital Agency | Logo Design, Web Development, SEO, Digital Marketing",
    template: "%s - TKVibes Digital Agency",
  },
  description:
    "TKVibes is a premier digital agency offering logo design, logo animation, website development, SEO services, Google Ads, Meta ads, n8n automation, and more. Your one-stop digital partner for brand growth.",
  keywords:
    "digital agency, logo design, website design, SEO services, Google My Business listing, Meta ads, Google Ads, n8n automation, digital marketing agency, brand identity",
  authors: [{ name: "TKVibes" }],
  robots: "index, follow",
  openGraph: {
    title: "TKVibes - Full-Service Digital Agency",
    description:
      "Logo design, web development, SEO, digital marketing & automation services. Transform your brand with TKVibes.",
    type: "website",
    url: "https://tkvibes.com/",
    images: ["https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200"],
  },
  twitter: {
    card: "summary_large_image",
    title: "TKVibes - Full-Service Digital Agency",
    description:
      "Transform your brand with professional logo design, web development, SEO, and digital marketing.",
  },
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${poppins.variable}`}>
      <body className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
        <ScrollToTop />
        <WhatsAppFloat />
      </body>
    </html>
  );
}