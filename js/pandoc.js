import "./pandoc.css";
import "./uuid.js";
import html from "./pandoc.html";
import { generateUUID } from "./uuid.js";

//https://github.com/georgestagg/pandoc-wasm
import { Pandoc } from "pandoc-wasm";

function render({ model, el }) {
  const _headless = model.get("headless");
  const pandoc = new Pandoc();
  pandoc.init().then(async (pandoc) => {
    const version = await pandoc.getVersion();
    model.set("about", {
      widget: "jupyter_anywidget_pandoc",
      pandoc_version: version,
    });
    //alert("Pandoc version is: " + version);
    model.set("response", { status: "ready" });
    model.save_changes();

    if (!_headless) {
      let el2 = document.createElement("div");
      el2.innerHTML = html;
      const uuid = generateUUID();
      el2.id = uuid;
      el.appendChild(el2);
    }

    model.on("change:doc_content", () => {
      const input_raw = model.get("doc_content");
      const input_format = model.get("input_format");
      const output_format = model.get("output_format");

      model.set("response", {
        status: "working on it...",
        input_format: input_format,
        output_format: output_format,
        input_raw: input_raw,
      });
      model.save_changes();

      async function handle_conversion(model, pandoc) {
        const result = await pandoc.run({
          text: input_raw,
          options: { from: input_format, to: output_format },
        });
        model.set("output_raw", result);
        model.set("response", { status: "completed", output_raw: result });
        model.save_changes();
        return result;
      }

      handle_conversion(model, pandoc).then((result) => {
        if (!_headless) {
          const img_el = el.querySelector('div[title="image-container"]');
          const dot_el = el.querySelector('pre[title="dot-container"]');
          dot_el.innerHTML = src;
          img_el.innerHTML = "Processing...";
          img_el.innerHTML = result;
        }
      });
    });
  });
}

export default { render };
