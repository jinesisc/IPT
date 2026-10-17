# IPT simulations

Models and simulations for IPT (International Physicists' Tournament) problems. 
One folder per problem, with shared constants and plot styling in `common/`.

Note: Most simulations are built from theoretical values and assumptions, but are
aimed to be tuned to real-life values post-experimentation. 

## Setup (once)

In the IDE terminal, with the project's `.venv` active:

```
pip install -r requirements.txt
```

## Running a problem

```
python main.py hourglass      # run one problem
python main.py list           # see what's available
```

Running `main.py` runs `DEFAULT`, set at the top of the file.
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
│       ├── data/            your experimental measurements (commited)
│       └── figures/         generated output (not committed)
└── requirements.txt
```

