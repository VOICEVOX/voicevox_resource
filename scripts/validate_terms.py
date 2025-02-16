# 各種利用規約の内容が整合しているかをチェックするスクリプト

import re
from pathlib import Path
import difflib
from dataclasses import dataclass
from typing import Literal


def main():
    terms = (
        Term(
            name="engine_text",
            title="VOICEVOX エンジン利用規約",
            path=Path("engine/README.md"),
            type="text",
        ),
        CoreTerm(
            name="core_text",
            title="VOICEVOX コアライブラリ利用規約",
            path=Path("core/README.md"),
            type="text",
        ),
        Term(
            name="vvm_markdown",
            title="VOICEVOX 音声モデル 利用規約",
            path=Path("vvm/README.md"),
            type="markdown",
        ),
        Term(
            name="vvm_text",
            title="VOICEVOX 音声モデル 利用規約",
            path=Path("vvm/README.txt"),
            type="text",
        ),
    )
    base_term = terms[0]
    target_terms = terms[1:]

    print("ファイルの存在確認")
    for term in terms:
        term.validate_file_exist()

    print("正規化の妥当性を確認")
    for term in terms:
        term.validate_normalized_content()

    print("内容の比較")
    base_content = base_term.normalized_content
    for target_term in target_terms:
        print(f"{base_term} vs {target_term}")
        target_content = target_term.normalized_content
        validate_content_difference(base_content, target_content)


@dataclass
class Term:
    name: str
    title: str
    path: Path
    type: Literal["markdown", "text"]

    def __repr__(self):
        return f"{self.name}"

    def validate_file_exist(self):
        assert self.path.is_file(), f"{self} がファイルではありません"
        assert self.path.exists(), f"{self} が存在しません"

    @property
    def content(self) -> str:
        with open(self.path, encoding="utf-8") as f:
            return f.read()

    @property
    def normalized_content(self) -> str:
        content = self.content

        # markdown特有の記法を削除
        if self.type == "markdown":
            content = content.replace("  \n", "\n")  # "  \n"をただの改行へ
            content = re.sub(r"\[|\]", "", content)  # リンクの[]を除去

        # text用の記法を削除
        elif self.type == "text":
            content = re.sub(r"、\n", "、", content)  # 読みやすくするための改行を削除

        # タイトル行を置き換え
        content = re.sub(
            rf"^# {self.title}", f"# 利用規約タイトル", content, flags=re.MULTILINE
        )

        return content

    def validate_normalized_content(self):
        # 正規化によって文字数が大きく変わらないことを確認
        content = self.content
        normalized_content = self.normalized_content
        rate = len(normalized_content) / len(content)
        assert (
            0.9 < rate < 1.1
        ), f"{self} の正規化により文字数が大きく変わっています: {rate}"


class CoreTerm(Term):
    @property
    def normalized_content(self) -> str:
        content = super().normalized_content

        trim_string = (
            "これは VOICEVOX コアライブラリです。\n"
            "https://github.com/VOICEVOX/voicevox_core\n\n"
            "---\n\n"
        )
        if trim_string in content:
            content = content.split(trim_string, 1)[1]

        return content


def validate_content_difference(base_content: str, target_content: str):
    diff = difflib.unified_diff(
        base_content.splitlines(),
        target_content.splitlines(),
    )
    diffs = list(diff)

    if len(diffs) == 0:
        return

    print("利用規約の内容が異なります：")
    diff_output = "\n".join(diffs)
    print(diff_output)

    raise Exception("利用規約の内容が異なります")


if __name__ == "__main__":
    main()
