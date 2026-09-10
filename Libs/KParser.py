# 余計な型ヒントや高度な正規表現は使いません。
# "{1.0, 5.0, 10.0}" ならリスト、"1.0" ならスカラにします。
# "1.0f" のような余計な文字が混じっても、数字部分だけ拾う簡易クリーニングを入れています。

class ParseError(ValueError):
    pass

class KParser:

    def __init__(self):
        pass

    def _clean_numeric_string(s):
        # 数字と記号だけを残す簡易クリーナー（例: "1.0f" -> "1.0"）
        t = ""
        for ch in s:
            if ch.isdigit() or ch in ".-+eE":
                t += ch
        return t
    
    def parse_cell(cell):
        """
        CSVセルから float または [float, ...] を返す。
        - "{1,2,3}" / "{1.0, 5.0}" のような形式はリストで返す
        - "1.0", "1e-3" はスカラで返す
        - "1.0f" 等も数字部分だけ残して解釈を試みる
        - "", None, "NA"/"nan"/"none"/"null" は None を返す
        """
        if cell is None:
            return None
    
        s = str(cell).strip()
        if s == "" or s.lower() in ("na", "nan", "none", "null"):
            return None
    
        if s.startswith("{") and s.endswith("}"):
            inner = s[1:-1]
            parts = inner.split(",")
            out = []
            for p in parts:
                t = p.strip()
                if t == "":
                    continue
                # まず素直にfloat化、ダメなら簡易クリーナーで再挑戦
                try:
                    out.append(float(t))
                except ValueError:
                    tt = _clean_numeric_string(t)
                    if tt == "":
                        raise ValueError("list item is not numeric: %r" % t)
                    out.append(float(tt))
            return out
    
        # スカラ
        try:
            return float(s)
        except ValueError:
            t = _clean_numeric_string(s)
            if t == "":
                raise ValueError("cell is not numeric: %r" % s)
            return float(t)
    
    def pair_dose_dist(dose, dist, allow_broadcast=False):
        """
        dose/dist から [(dose, dist), ...] を作る。
        - 両方リスト: 長さ一致必須
        - 両方スカラ: 1要素のリストで返す
        - 片方がリスト・片方がスカラ:
            - allow_broadcast=True ならスカラを繰り返して対応
            - False なら例外
        - どちらか None は例外（仕様に応じて変えてOK）
        """
        if dose is None or dist is None:
            raise ValueError("dose or dist is None")
    
        dose_is_list = isinstance(dose, (list, tuple))
        dist_is_list = isinstance(dist, (list, tuple))
    
        if dose_is_list and dist_is_list:
            if len(dose) != len(dist):
                raise ValueError("length mismatch: dose=%d dist=%d" % (len(dose), len(dist)))
            return [(float(d), float(x)) for d, x in zip(dose, dist)]
    
        if (not dose_is_list) and (not dist_is_list):
            return [(float(dose), float(dist))]
    
        if not allow_broadcast:
            raise ValueError("mixing list and scalar is not allowed (set allow_broadcast=True to enable broadcasting)")
    
        if dose_is_list and (not dist_is_list):
            return [(float(d), float(dist)) for d in dose]
    
        if dist_is_list and (not dose_is_list):
            return [(float(dose), float(x)) for x in dist]
    
        # 通らない想定
        raise RuntimeError("unexpected state in pair_dose_dist")
    
if __name__ == "__main__":
    # 動作確認用
    import sys
    import pandas as pd
    df = pd.read_csv(sys.argv[1])
    
    parser = KParser()
    
    for row in df.iterrows():
        idx, data = row
        try:
            dose = parser.parse_cell(data['dose_ds'])
            dist = parser.parse_cell(data['dist_ds'])
    
            values=parser.pair_dose_dist(dose, dist)
            print(values)
    
            df.at[idx, 'dose'] = dose
            df.at[idx, 'dist'] = dist
        except ValueError as e:
            print("Error in row %d: %s" % (idx, e), file=sys.stderr)
            sys.exit(1)
    
    dose_list = [1,5,10]
    dist_list = [100,110,120]
    print(parser.pair_dose_dist(dose_list, dist_list))