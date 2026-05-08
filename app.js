const grid = document.getElementById("moduleGrid");
const inspector = document.getElementById("inspector");
const seoList = document.getElementById("seoList");

const iconMap = {
  dial: "◉",
  tape: "▣",
  scale: "⚖",
  lens: "⌕",
  rail: "╫",
  filter: "⌬",
  frame: "▤",
  boot: "▰"
};

function injectBootSequence() {
  const boot = document.getElementById("boot");
  if (!boot) return;

  boot.innerHTML = `
    <div class="boot-box">
      <p class="boot-title">DEADPUNK_OS v0.8</p>
      <ul class="boot-lines">
        <li><span>[OK]</span> mounting profile.readme</li>
        <li><span>[OK]</span> loading featured modules</li>
        <li><span>[OK]</span> found 8 public artifacts</li>
        <li><span>[WARN]</span> portfolio template not found</li>
        <li><span>[OK]</span> applying tape-based runtime</li>
        <li><span>[BOOT]</span> starting workbench</li>
      </ul>
      <div class="boot-progress" aria-hidden="true">
        <div class="boot-progress-fill"></div>
      </div>
      <p class="boot-percent">loading: [##########------]</p>
    </div>
  `;

  const style = document.createElement("style");
  style.textContent = `
    .boot-box {
      width: min(640px, 86vw);
      padding: 24px;
      border: 1px solid var(--line);
      background: #12120e;
      color: var(--green);
      box-shadow: 0 0 40px var(--shadow), inset 0 0 24px rgba(138, 163, 111, 0.06);
      line-height: 1.6;
    }

    .boot-title {
      margin: 0 0 18px;
      color: var(--text);
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }

    .boot-lines {
      list-style: none;
      margin: 0;
      padding: 0;
      min-height: 174px;
    }

    .boot-lines li {
      opacity: 0;
      transform: translateY(4px);
      animation: boot-line-in 0.22s steps(2, end) forwards;
    }

    .boot-lines li:nth-child(1) { animation-delay: 0.35s; }
    .boot-lines li:nth-child(2) { animation-delay: 0.85s; }
    .boot-lines li:nth-child(3) { animation-delay: 1.35s; }
    .boot-lines li:nth-child(4) { animation-delay: 1.9s; }
    .boot-lines li:nth-child(5) { animation-delay: 2.45s; }
    .boot-lines li:nth-child(6) { animation-delay: 3.05s; }

    .boot-lines span {
      display: inline-block;
      width: 74px;
      color: var(--hot);
    }

    .boot-progress {
      height: 14px;
      margin-top: 18px;
      border: 1px solid var(--line);
      background: rgba(0, 0, 0, 0.28);
      overflow: hidden;
    }

    .boot-progress-fill {
      height: 100%;
      width: 0;
      background: repeating-linear-gradient(90deg, var(--hot), var(--hot) 8px, transparent 8px, transparent 12px);
      animation: boot-progress 3.65s steps(16, end) forwards;
    }

    .boot-percent {
      margin: 10px 0 0;
      color: var(--muted);
      font-size: 0.86rem;
    }

    @keyframes boot-line-in {
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes boot-progress {
      to { width: 100%; }
    }
  `;
  document.head.appendChild(style);
}

function renderModules() {
  grid.innerHTML = PROJECTS.map((project, index) => `
    <button class="module" data-id="${project.id}" style="--tilt:${index % 2 === 0 ? "-1.5deg" : "1.2deg"}">
      <span class="module-icon">${iconMap[project.icon] || "□"}</span>
      <span class="module-name">${project.module}</span>
      <span class="module-type">${project.type}</span>
    </button>
  `).join("");

  document.querySelectorAll(".module").forEach((button) => {
    button.addEventListener("click", () => {
      const project = PROJECTS.find((item) => item.id === button.dataset.id);
      openProject(project);
      document.querySelectorAll(".module").forEach((item) => item.classList.remove("selected"));
      button.classList.add("selected");
    });
  });
}

function openProject(project) {
  if (!project) return;

  inspector.innerHTML = `
    <p class="stamp">INSPECTING: ${project.module}</p>
    <h1>${project.title}</h1>
    <p class="subtitle">${project.subtitle || project.type}</p>

    <dl class="specs">
      <div><dt>TYPE</dt><dd>${project.type}</dd></div>
      <div><dt>JOB</dt><dd>${project.job}</dd></div>
      <div><dt>PROBLEM</dt><dd>${project.problem}</dd></div>
      <div><dt>OUTPUT</dt><dd>${project.output}</dd></div>
      <div><dt>STATUS</dt><dd>${project.status}</dd></div>
    </dl>

    <div class="actions">
      <a href="${project.repo}" target="_blank" rel="noreferrer">open repo</a>
      <button type="button" id="copyModule">copy module name</button>
    </div>
  `;

  const copyButton = document.getElementById("copyModule");
  copyButton?.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(project.module);
      copyButton.textContent = "copied";
      setTimeout(() => copyButton.textContent = "copy module name", 1200);
    } catch {
      copyButton.textContent = "copy failed";
      setTimeout(() => copyButton.textContent = "copy module name", 1200);
    }
  });
}

function renderSeoFallback() {
  seoList.innerHTML = PROJECTS.map(project => `
    <li>
      <a href="${project.repo}">${project.title}</a>: ${project.job}
    </li>
  `).join("");
}

injectBootSequence();
renderModules();
renderSeoFallback();

setTimeout(() => {
  document.getElementById("boot")?.classList.add("hidden");
}, 4000);

if (PROJECTS[0]) {
  const first = document.querySelector(".module");
  first?.classList.add("selected");
  openProject(PROJECTS[0]);
}
