# IPT simulations

Models for IPT (International Physicists' Tournament) problems. One folder per
problem, with shared constants and plot styling in `common/`.

## Setup (once)

In PyCharm's terminal, with the project's `.venv` active:

```
pip install -r requirements.txt
```

## Running a problem

```
python main.py hourglass      # run one problem
python main.py list           # see what's available
```

Or press PyCharm's green Run button on `main.py` (runs `DEFAULT`, set at the top of the file).
Figures are saved into that problem's own `figures/` folder.

## Layout

```
IPT/
├── main.py                  launcher: python main.py <problem>
├── common/
│   ├── constants.py         G, MU0, air/water properties ...
│   └── plotting.py          shared plot style, colors, save_figure()
├── problems/
│   └── p01_magnetic_hourglass/
│       ├── model.py         the simulation (has a main())
│       ├── README.md        problem statement, assumptions, parameters to fit
│       ├── data/            your experimental measurements (commit these)
│       └── figures/         generated output (not committed)
└── requirements.txt
```

## Adding a problem

1. Create `problems/pNN_short_name/` containing an empty `__init__.py` and a `model.py` with a `main()` function.
2. Add a line to `PROBLEMS` in `main.py`.
3. Keep physics specific to that problem inside its folder. Move something into `common/`
   only once a second problem actually needs it.
