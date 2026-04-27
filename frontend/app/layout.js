import "./globals.css";

export const metadata = {
  title: "BriefForge",
  description: "Sheet metal engineering briefing agent",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
