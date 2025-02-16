# voicevox_resource

VOICEVOX 用のリソースファイル置き場

## キャラクター情報（character_info ディレクトリ）

ディレクトリ名が`[キャラ名]_[speaker_uuid]`になっていたり、作業用の中間画像ファイルが含まれていたりします。
エンジン側で求められている情報と違う点は `script/clean_character_info.py` で修正可能です。

## キャラクターの得意なピッチ情報

`metas.json`にキャラクター各スタイルの最適なピッチ区間が記録されています。
エンジン側がアップデートなどにより、ピッチ区間が変更される場合、**エンジンを起動して**、

```bash
python scripts/gather_pitch_range.py
```

を実行して、作り直すことが可能です。

使用するテキストデータは芥川龍之介の「羅生門」（[パブリックドメイン](https://ja.wikisource.org/wiki/%E7%BE%85%E7%94%9F%E9%96%80)）。

## 画像ファイル

アイコン画像は `scripts/resize.sh` を使って 256x256 のサイズにします。  
立ち絵画像は縦幅が 500 になるように手動で調整しています。

## タイポチェック

[typos](https://github.com/crate-ci/typos) を使ってタイポのチェックを行っています。
[typos をインストール](https://github.com/crate-ci/typos#install) した後

```bash
typos
```

## ライセンス

### scripts ディレクトリのファイル

MIT ライセンス

### それ以外のファイル

VOICEVOX の開発のための利用のみ許可されます。
異なるライセンスを取得したい場合は、ヒホ（twitter: @hiho_karuta）に求めてください。
