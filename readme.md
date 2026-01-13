# ResonanceTables to SQLite DB Converter

This repository provides a Python-based utility to parse and ingest the evaluated (or selected) Resonance Parameters, Thermal Cross Sections, and MACS from the [arjankoning1/resonancetables](https://github.com/arjankoning1/resonancetables) repository into a **SQLite database**.


## 2. Database Schema

### Key Tables

| Table | Description |
| --- | --- |
| `nuclides` | Contains unique nuclei defined by `Z`, `A`, and `metastable` state. Includes chemical symbols (e.g., `Hf`). |
| `sources` | The origin of the data (e.g., `Mughabghab-2018`, `JENDL-5.0`, `TENDL-2025`). |
| `categories` | The energy domain or measurement type (`resonance`, `thermal`, `macs`). |
| `reaction_types` | Specific reaction channels or parameters (e.g., `ng`, `nf`, `D0`, `S1`, `na-g`). |
| `data_table` | The core table storing `value`, `dValue` (uncertainty), and `ratio`. |

## 3. Data Contexts & Physical Meaning

See the details in [RESONANCETABLES-2.2](https://nds.iaea.org/talys/tutorials/resonancetables.pdf) and [arjankoning1/resonancetables](https://github.com/arjankoning1/resonancetables).

This script automatically maps the directory structure to a metadata:

| Category | Typical Quantities | Description |
| --- | --- | --- |
| **Resonance** | `D0`, `S0`, `S1`, `gamgam0` | Average resonance parameters (level spacings, strength functions). |
| **Thermal** | `ng`, `nf`, `el`, `tot` | Cross sections at  (). |
| **MACS** | `ng` (macs) | Maxwellian-averaged cross sections (crucial for s-process nucleosynthesis). |


## 5. Requirements

* Python 3.10+
* SQLAlchemy 2.0+
* SQLite 3

## 6. Usage

1. **Clone the Data Source**:
Clone the original data repository to your local machine.
```bash
git clone https://github.com/arjankoning1/resonancetables.git
```


2. **Configure Paths**:
Update the `DATA_ROOT` in `config.py` to point to your local clone.

3. **Run the Ingestor**:
```bash
python schema.py
python ingest.py

```




