# Adding a Custom Block to a GNU Radio OOT Module — Checklist

Reference workflow for `gr-my_h_line_tools`. Environment: Radioconda on
Windows, Anaconda Prompt with `radioconda` activated.


## 1. Scaffold the block (new blocks only)

Skip this step if you're editing a block that already exists in the module.
In anaconda prompt: 

cd <to working directory>
gr_modtool add -t general <block_name>

*In my case, I named my working directory "my_h_line_tools"

- `-t general` → maps to `gr.basic_block` (variable input/output rate).
  Use `-t sync` instead for a `gr.sync_block` (strict 1:1 rate).
- Language prompt → choose Python
- Argument list prompt → enter your constructor's args, e.g.:
  `vector_size, apply_cal=False, cal_path='h_line_cal.csv'`
- QA code prompt → optional, fine to accept

**Immediately verify naming didn't drift** (has happened before):

Anaconda prompt:

type python\my_h_line_tools\<block_name>.py
type python\my_h_line_tools\__init__.py

Confirm the `class <name>(gr.basic_block):` line and the
`from .<name> import <name>` line in `__init__.py` both match the name
you actually intend to use. If they don't match your code, either rename
your class to match, or edit both files consistently.


## 2. Write/paste the block's Python code

Edit (replace entirely, don't merge with the generated skeleton):

python\my_h_line_tools\<block_name>.py
*I have a separate directory connected to github for edits apart from the GRC 
working directory. For this step, I simply replace the files in this working
directory with the new ones (keeping the same name of course). 


## 3. Write/edit the block's GRC YAML

File:

grc\my_h_line_tools_<block_name>.block.yml


Checklist for the YAML itself:
- [ ] `id:` matches `<module_name>_<block_name>`
- [ ] `templates.make` — positional args match your `__init__` signature
      **exactly**, same count, same order
- [ ] `templates.callbacks` — one entry per `set_X()` method you want
      live-controllable from a GUI widget (only needed for values that
      change while running, not one-time constructor args)
- [ ] `parameters` — one entry per constructor arg, **plus** one entry
      for any variable referenced only in `callbacks` (e.g. a value that
      isn't passed to the constructor but is set live via callback)
- [ ] `inputs` / `outputs` — dtype and `vlen` match your `in_sig`/`out_sig`
- [ ] `documentation` — use block literal (`|-`) style if the text
      contains any colons, to avoid YAML parse errors
- [ ] No tabs, consistent indentation


## 4. Build and install

First time configuring in a given `build/` folder:

cd gr-my_h_line_tools\build
cmake -G "Ninja" -DCMAKE_INSTALL_PREFIX="C:\Users\Daniel\AppData\Local\miniconda3\envs\radioconda\Library" -DGR_PYTHON_DIR="C:\Users\Daniel\AppData\Local\miniconda3\envs\radioconda\Lib\site-packages" ..

Every time after editing Python/YAML source files:

Anaconda prompt:

ninja
ninja install

*`cmake` only needs to be re-run if you scaffold a brand-new block —
adding a new source file changes what CMake needs to track. Editing an
existing file's contents only needs `ninja` + `ninja install` after updating
the file.


## 5. Verify the install landed correctly

Anaconda prompt:

python -c "from gnuradio import my_h_line_tools; print(my_h_line_tools)"

Should import with no error.


dir "C:\Users\Daniel\AppData\Local\miniconda3\envs\radioconda\Library\share\gnuradio\grc\blocks" | findstr <block_name>

Should show the installed `.block.yml`.


## 6. Restart GRC and test

- Fully close and reopen GNU Radio Companion (new/edited blocks are only
  picked up on startup)
- Search the block palette for your block name
- Drag into a test flowgraph, confirm parameters/ports look correct
- Check GRC widget **Default Values** if a toggle/parameter behaves
  unexpectedly on startup — GRC's saved widget default can silently
  override your Python constructor's default


## Common errors and fixes

| Symptom | Likely cause |
|---|---|
| `ImportError: cannot import name 'X'` | Class name in your `.py` doesn't match what `__init__.py` imports |
| Block missing from GRC palette | YAML failed to parse (check indentation/colons), or `ninja install` wasn't re-run after editing |
| `file cannot create directory: C:/Program Files...` | `CMAKE_INSTALL_PREFIX` not set to the conda environment |
| Python files land under `Library\lib\site-packages` instead of `Lib\site-packages` | `GR_PYTHON_DIR` not set explicitly |
| `TypeError: too many/few positional arguments` | `templates.make` arg count/order doesn't match `__init__` signature |
| Laggy/stuck GUI display for a variable-rate block | Block should be `gr.basic_block` + `general_work()` with explicit `self.consume()`, not `gr.sync_block` |
| `MSBuild : error MSB1009` | Stale CMake cache from a previous generator; delete `build/` and reconfigure |
| `CMake Error: ... VCTargetsPath` | Use `-G "Ninja"` instead of the default MSBuild generator |
