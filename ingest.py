
from sqlalchemy import select
from schema import data_table, sources, nuclides, reaction_types, categories
from config import engine, DATA_ROOT


def get_or_create_id(conn, table, unique_col, value, **other_cols):
    """一意なレコードのIDを取得、なければ作成"""
    stmt = select(table.c.id).where(unique_col == value)
    result = conn.execute(stmt).fetchone()
    if result:
        return result[0]
    
    ins = table.insert().values({unique_col.name: value, **other_cols})
    return conn.execute(ins).lastrowid

from sqlalchemy import select, insert

def get_or_create_nuclide(conn, z, a, iso, n_string, metastable):
    """
    Z, A, metastable の組み合わせで核種を特定し、IDを返す。
    存在しない場合は新規作成する。
    """
    # 1. まず既存の核種があるか検索 (UniqueConstraintに基づいた検索)
    query = select(nuclides.c.nuclide_id).where(
        (nuclides.c.Z == z) & 
        (nuclides.c.A == a) & 
        (nuclides.c.metastable == metastable)
    )
    result = conn.execute(query).fetchone()

    if result:
        return result[0]

    # 2. 存在しない場合は挿入
    ins_stmt = insert(nuclides).values(
        Z=z,
        A=a,
        Iso=iso,
        nuclide=n_string,
        metastable=metastable
    )
    res = conn.execute(ins_stmt)
    return res.lastrowid

def parse_line(line):
    """データ行をパース (Z A Liso Value dValue Ratio Nuclide)"""
    parts = line.split()
    if len(parts) < 7: return None
    try:
        return {
            "z": int(parts[0]),
            "a": int(parts[1]),
            "liso": int(parts[2]),
            "value": float(parts[3]),
            "dvalue": float(parts[4]),
            "ratio": float(parts[5]),
            "name": parts[6]
        }
    except ValueError:
        return None

def parse_nuclide_name(n_string):
    """
    symbol(例: 'Hf178n', 'Am242m') から Iso と metastable を判定する
    """
    # 末尾が 'n' や 'm' などで終わる場合の簡易判定
    # 実際のデータ仕様に合わせて調整してください
    metastable = 0
    if n_string.endswith('n'):
        metastable = 2
    elif n_string.endswith('m'):
        metastable = 1
    elif n_string.endswith('p'): # 稀にあるケース
        metastable = 2

    # 記号部分 (例: 'Hf178n' -> 'Hf')
    # 数字以降を除去する正規表現など
    import re
    match = re.match(r"([a-zA-Z]+)", n_string)
    iso = match.group(1) if match else n_string
    
    return iso, metastable


# --- メイン処理 ---
def main():
    # 対象とするカテゴリ（ディレクトリ名）
    target_categories = ["resonance", "thermal", "macs"]

    with engine.begin() as conn:
        for cat_name in target_categories:
            cat_dir = DATA_ROOT / cat_name
            if not cat_dir.exists():
                continue

            # カテゴリIDの取得 (resonance, thermal, macs)
            cat_id = get_or_create_id(conn, categories, categories.c.name, cat_name)

            # reactionディレクトリ (D0, ng, na-g, nf 等) を巡回
            for react_dir in cat_dir.iterdir():
                if not react_dir.is_dir():
                    continue
                
                react_name = react_dir.name  # 例: D0, ng, na-g
                all_dir = react_dir / "all"
                if not all_dir.exists():
                    continue

                # 反応IDの取得
                react_id = get_or_create_id(conn, reaction_types, reaction_types.c.name, react_name)
                print(f"Processing: [{cat_name}] -> {react_name}")

                for file_path in all_dir.glob("*.txt"):
                    # 特定のファイルを除外
                    if any(x in file_path.name for x in ["EXFOR", "selected"]):
                        continue

                    # ソース名の抽出
                    # 'jendl5.0_D0.txt' -> 'jendl5.0'
                    # 'Astral_macs.txt' -> 'Astral'
                    source_raw = file_path.stem.split('_')[0]
                    source_id = get_or_create_id(conn, sources, sources.c.source_name, source_raw)
                    
                    records_to_insert = []
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            # ヘッダーや空行をスキップ
                            if not line or line.startswith(('#', 'Z', '[')):
                                continue
                            
                            data = parse_line(line)
                            if not data:
                                continue

                            # 核種情報の抽出とID取得
                            iso, m_state = parse_nuclide_name(data['name'])
                            nuc_id = get_or_create_nuclide(
                                conn, 
                                z=data['z'], 
                                a=data['a'], 
                                iso=iso, 
                                n_string=data['name'], 
                                metastable=m_state
                            )
                            
                            records_to_insert.append({
                                "nuclide_id": nuc_id,
                                "source_id": source_id,
                                "category_id": cat_id,
                                "reaction_id": react_id,
                                "quantity_type": react_name, # 必要に応じて保持
                                "liso": data['liso'],
                                "value": data['value'],
                                "dvalue": data['dvalue'],
                                "ratio": data['ratio']
                            })
                    
                    # バルクインサート
                    if records_to_insert:
                        # resonance_parameters から名称変更した nuclear_data 等のテーブル名に合わせてください
                        conn.execute(data_table.insert(), records_to_insert)
                        print(f"  Loaded {len(records_to_insert)} entries from {file_path.name}")

if __name__ == "__main__":
    main()