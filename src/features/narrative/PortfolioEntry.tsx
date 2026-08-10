import Link from "next/link";

export default function PortfolioEntry() {
  return (
    <main className="portfolio-entry">
      <nav aria-label="Portfolio" className="portfolio-nav">
        <span className="portfolio-wordmark">Yoreny</span>
        <span>Portfolio / CV</span>
      </nav>
      <section className="portfolio-intro">
        <p className="portfolio-kicker">RESEARCH · DATA · INTERACTION</p>
        <h1>Personal portfolio</h1>
        <p>This route is reserved for the personal CV and portfolio. Melbourne Urban Pulse is presented as one inspectable research project within it.</p>
        <Link className="portfolio-project" href="/projects/melbourne-urban-pulse">
          <span>Featured research project</span>
          <strong>Melbourne Urban Pulse</strong>
          <span>Open project narrative →</span>
        </Link>
      </section>
    </main>
  );
}
