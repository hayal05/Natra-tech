// Lightweight admin collection editor; no dependencies.
(() => {
  const form = document.getElementById("site-editor");
  if (!form) return;
  const limits = {stats:{value:40,label:100},projects:{name:120,tags:180,year:12,variant:1},services:{title:120,tagline:240,detail:1000},values:{title:100,description:600}};
  function renumber(section) {
    const group = section.dataset.collection;
    const rows = [...section.querySelectorAll("[data-entry]")];
    section.querySelector('[name="'+group+'_count"]').value = rows.length;
    rows.forEach((row,index) => {
      const title = row.querySelector(".content-entry-header strong");
      if (title) title.textContent = group.charAt(0).toUpperCase()+group.slice(1)+" #"+(index+1);
      row.querySelectorAll("[data-field]").forEach(el=>{
        const field=el.dataset.field;
        el.name=group+"_"+index+"_"+field;
        el.id=el.name;
        if(limits[group][field]) el.maxLength=limits[group][field];
        const label=el.closest("div")?.querySelector("label");
        if(label) label.htmlFor=el.id;
      });
    });
    const add=section.querySelector("[data-add]");
    if(add) add.disabled=rows.length>=Number(section.dataset.limit);
  }
  document.querySelectorAll("[data-collection]").forEach(section=>{
    renumber(section);
    section.querySelector("[data-add]").addEventListener("click",()=>{
      if(section.querySelectorAll("[data-entry]").length>=Number(section.dataset.limit)) return;
      const fragment=section.querySelector("template").content.cloneNode(true);
      section.querySelector("[data-rows]").appendChild(fragment);
      renumber(section);
    });
    section.addEventListener("click",e=>{
      const button=e.target.closest("[data-remove]");
      if(!button) return;
      button.closest("[data-entry]")?.remove();
      renumber(section);
    });
  });
})();