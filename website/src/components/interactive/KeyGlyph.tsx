export default function KeyGlyph({index}: {index: number}) {
  const paths = [
    <><circle cx="20" cy="20" r="11"/><path d="M20 4v8m0 16v8M4 20h8m16 0h8m-8-11 5-5"/></>,
    <><path d="M9 13V8h17m5 9v15H14M5 19v12h6m9-23v14m-7-7h14"/></>,
    <><path d="M7 10h20v16H15l-7 6v-6H7zM14 15h19v16H22"/></>,
    <><path d="M7 10h20v16H15l-7 6v-6H7zM14 15h19v16H22"/></>,
    <><path d="M7 10h20v16H15l-7 6v-6H7zM14 15h19v16H22"/></>,
    <><path d="M7 10h20v16H15l-7 6v-6H7zM14 15h19v16H22"/></>,
    <><path d="M14 10h19M14 20h19M14 30h19M6 9h2v2H6zM6 19h2v2H6zM6 29h2v2H6z"/></>,
    <><path d="M8 11h24v21H8zM14 22l5 5 13-15M5 6h9"/></>,
    <><path d="M8 11h24v21H8zM15 18l10 10m0-10L15 28M5 6h9"/></>,
    <><path d="m9 10 10 10L9 30m14 0h11M5 5h30"/></>,
    <><path d="M6 17v6m6-13v20m8-25v30m8-25v20m6-13v6"/></>,
    <><path d="M8 7h12v9H8zm0 19h12v9H8zm18-9h10v9H26zM14 16v10m0-5h12"/></>,
    <><path d="M10 10h20v20H10zM15 15h10v10H15zM15 5v5m10-5v5M15 30v5m10-5v5M5 15h5m-5 10h5m20-10h5m-5 10h5"/></>,
  ];
  return <svg viewBox="0 0 40 40" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="square" strokeLinejoin="miter" aria-hidden="true">{paths[index]}</svg>;
}
