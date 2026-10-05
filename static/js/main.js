// Sticky header, mobile menu, and scroll reveal.
(function () {
  const header = document.querySelector(".site-header");
  const toggle = document.querySelector(".nav-toggle");
  const links = document.querySelector(".nav-links");

  if (header && toggle && links) {  // admin pages use their own header
    const onScroll = () => header.classList.toggle("is-solid", window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });

    function setMenu(open) {
      toggle.setAttribute("aria-expanded", open);
      links.classList.toggle("is-open", open);
      document.body.style.overflow = open ? "hidden" : "";
    }
    toggle.addEventListener("click", () => setMenu(toggle.getAttribute("aria-expanded") !== "true"));
    links.addEventListener("click", (e) => e.target.closest("a") && setMenu(false));
    document.addEventListener("keydown", (e) => e.key === "Escape" && setMenu(false));
  }

  // Thumbnails: fall back to the smaller YouTube image when the max-res one doesn't exist.
  document.querySelectorAll("img[data-fallback]").forEach((img) => {
    const swap = () => { const fb = img.dataset.fallback; if (fb) { delete img.dataset.fallback; img.src = fb; } };
    img.addEventListener("error", swap);
    if (img.complete && img.naturalWidth === 0) swap();
  });

  // Video window: the player loads only when clicked (nothing from YouTube runs before that).
  document.querySelectorAll(".video-frame[data-video-id]").forEach((frame) => {
    frame.addEventListener("click", (e) => {
      e.preventDefault();  // without JavaScript the link simply opens YouTube
      const iframe = document.createElement("iframe");
      iframe.src = "https://www.youtube-nocookie.com/embed/" + encodeURIComponent(frame.dataset.videoId) +
        "?autoplay=1&rel=0&modestbranding=1";
      iframe.title = frame.dataset.title || "Video";
      iframe.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
      iframe.allowFullscreen = true;
      iframe.referrerPolicy = "strict-origin-when-cross-origin";
      const box = document.createElement("div");
      box.className = "video-frame is-playing";
      box.appendChild(iframe);
      frame.replaceWith(box);
      iframe.focus();
    });
  });

  const items = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window)) return items.forEach((el) => el.classList.add("is-visible"));
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add("is-visible"); io.unobserve(e.target); }
    });
  }, { threshold: 0.12 });
  items.forEach((el) => io.observe(el));
})();
