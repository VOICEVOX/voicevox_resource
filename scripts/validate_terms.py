# 各種利用規約の内容が整合しているかをチェックするスクリプト

import difflib
import re
from dataclasses import dataclass
from pathlib import Path
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
    check_file_exists(terms)

    print("正規化の妥当性を確認")
    check_normalized_content(terms)

    print("内容の比較")
    compare_contents(base_term, target_terms)


@dataclass
class Term:
    name: str
    title: str
    path: Path
    type: Literal["markdown", "text"]

    def __repr__(self):
        return f"{self.name}"

    @property
    def content(self) -> str:
        with open(self.path, encoding="utf-8") as f:
            return f.read()

    @property
    def normalized_content(self) -> str:
        content = self.content
        if self.type == "markdown":
            content = self._trim_markdown_content(content)
        elif self.type == "text":
            content = self._trim_text_content(content)
        content = self._trim_title(content)
        return content

    def _trim_markdown_content(self, content: str) -> str:
        """markdown特有の記法を削除"""
        content = content.replace("  \n", "\n")  # "  \n"をただの改行へ
        content = re.sub(r"\[|\]", "", content)  # リンクの[]を除去
        return content

    def _trim_text_content(self, content: str) -> str:
        """text用の記法を削除"""
        content = re.sub(r"、\n", "、", content)  # 読みやすくするための改行を削除
        return content

    def _trim_title(self, content: str) -> str:
        """タイトル行を置き換え"""
        content = re.sub(
            rf"^# {self.title}", f"# 利用規約タイトル", content, flags=re.MULTILINE
        )
        return content


class CoreTerm(Term):
    @property
    def normalized_content(self) -> str:
        content = super().normalized_content

        CORE_HEADER_TEXT = (
            "これは VOICEVOX コアライブラリです。\n"
            "https://github.com/VOICEVOX/voicevox_core\n\n"
            "---\n\n"
        )
        if CORE_HEADER_TEXT in content:
            content = content.split(CORE_HEADER_TEXT, 1)[1]

        return content


def check_file_exists(terms: tuple[Term, ...]):
    for term in terms:
        assert term.path.is_file(), f"{term} がファイルではありません"
        assert term.path.exists(), f"{term} が存在しません"


def check_normalized_content(terms: tuple[Term, ...]):
    """正規化によって文字数が大きく変わらないことを確認する"""
    for term in terms:
        content = term.content
        normalized_content = term.normalized_content
        rate = len(normalized_content) / len(content)
        assert (
            0.9 < rate < 1.1
        ), f"{term} の正規化により文字数が大きく変わっています: {rate}"


def compare_contents(base_term: Term, target_terms: tuple[Term, ...]):
    base_content = base_term.normalized_content
    for target_term in target_terms:
        print(f"{base_term} vs {target_term}")
        target_content = target_term.normalized_content
        check_content_diff(base_content, target_content)


def check_content_diff(base_content: str, target_content: str):
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
