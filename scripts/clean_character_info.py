# character_infoディレクトリの中身を、エンジン側が求める形式に修正するスクリプト

import argparse
import shutil
from pathlib import Path
from uuid import UUID

parser = argparse.ArgumentParser()
parser.add_argument(
    "--character_info_dir",
    type=Path,
    default=Path("./character_info"),
    help="character_infoディレクトリのパス。デフォルト値は`./character_info`",
)
parser.add_argument(
    "--output_dir",
    type=Path,
    default=None,
    help="出力先ディレクトリ。`character_info_dir`と同じパスの場合は上書きする。デフォルト値は`./character_info`",
)
args = parser.parse_args()

character_info_dir: Path = args.character_info_dir
output_dir: Path = args.output_dir if args.output_dir else character_info_dir


def verify_uuid4(uuid_string: str) -> bool:
    try:
        UUID(uuid_string, version=4)
    except ValueError:
        return False
    return True


if not character_info_dir.exists():
    raise Exception(f"エラー：{character_info_dir} が存在しません。")

# output_dirにコピーする
if character_info_dir != output_dir:
    if output_dir.exists():
        raise Exception(f"エラー：{output_dir} は既に存在します。")
    shutil.copytree(character_info_dir, output_dir)

# キャラクターごとのディレクトリ名から_以前の文字列があれば取り除く
for dir_path in output_dir.glob("*"):
    dir_name = dir_path.name
    if "_" in dir_name:
        new_dir_name = dir_name.split("_")[-1]
        assert verify_uuid4(
            new_dir_name
        ), f"エラー：{new_dir_name} がUUID4形式ではありません。"
        dir_path.rename(output_dir / new_dir_name)

# *.png_largeファイルを消去する
for png_large_path in output_dir.rglob("*.png_large"):
    png_large_path.unlink()
