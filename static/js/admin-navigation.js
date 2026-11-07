// Admin sidebar navigation — isolated from the public site menu.
(() => {
  const shell = document.querySelector(".nt-admin-shell");
  if (!shell) return;
  const trigger = shell.querySelector("[data-admin-toggle]");
  const sidebar = shell.querySelector(".nt-admin-sidebar");
  const closeButtons = shell.querySelectorAll("[data-admin-close]");
  const mobile = window.matchMedia("(max-width: 900px)");
  const setOpen = (open, restoreFocus = false) => {
    const enabled = open && mobile.matches;
    shell.classList.toggle("is-open", enabled);
    document.body.classList.toggle("nt-admin-menu-open", enabled);
    trigger.setAttribute("aria-expanded", String(enabled));
    trigger.setAttribute("aria-label", enabled ? "Close admin navigation" : "Open admin navigation");
    if (enabled) sidebar.querySelector(".nt-admin-close")?.focus();
    else if (restoreFocus) trigger.focus();
  };
  trigger.addEventListener("click", () => setOpen(!shell.classList.contains("is-open")));
  closeButtons.forEach(button => button.addEventListener("click", () => setOpen(false, true)));
  sidebar.querySelectorAll("a").forEach(link => link.addEventListener("click", () => setOpen(false)));
  document.addEventListener("keydown", e => {
    if (e.key === "Escape" && shell.classList.contains("is-open")) setOpen(false, true);
    if (e.key === "Tab" && shell.classList.contains("is-open")) {
      const focusable = [...sidebar.querySelectorAll('a[href], button:not([disabled])')];
      if (!focusable.length) return;
      const first = focusable[0], last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });
  mobile.addEventListener("change", () => setOpen(false));
})();
