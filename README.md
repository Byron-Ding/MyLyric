# MyLyric
A python modual for processing and analysising Lrc files. 


The Library is already on pipe.


```shell
pip install MyLyric
```

Then just use this to import the library.
```python
import MyLyric
```

There are 5 class under the Library.
```python
from MyLyric import Lyric_Time_tab
from MyLyric import Lyric_character
from MyLyric import Lyric_file
from MyLyric import Lyric_line
from MyLyric import Lyric_line_content
```

* Lyric_file is for the total lyric file analysising
  
* Lyric_character is for each character, with pronounciation

* Lyric_line is Lyric_Time_tab + Lyric_line_content 
> Coorespond to each line of the file

* Lyric_line_content is formed by lyric characters with other information
> The cooresponding part is the lyric after [mm:ss:mm]

* Lyric_Time_tab is the time tab
> The cooresponding part is [mm:ss:mm]

A stand lyric format is like
```Lyric
[ti:ブルーバード (青鸟) (《火影忍者 疾风传》TV动画第274-297集片头曲)]
[ar:生物股长 (いきものがかり)]
[al:ブルーバード (青鸟)]
[by:]
[offset:0]
[kana:11111し1みず1の1よし1き1きょく1みず1の1よし1き2はばた1もど1い1め1ざ1あお1あお1そら1かな1おぼ1せつ1いま1いだ1かん1じょう1いま1こと1ば1か1み1ち1せ1かい2ゆめ1め1ざ1は1ね1ひろ1と1た2はばた1もど1い1め1ざ1しろ1しろ1くも1つ1ぬ1し1ふ1き1あお1あお1そら1あお1あお1そら1あお1あお1そら1あい1そ1つ1おと1さ1ふる1まど1こわ1み1あ1す1ふ1かえ1たか1な1こ1どう1こ1きゅう2あず1まど1け1と1た1か1だ1て1い1とお1とお1こえ1まぶ1て1にぎ1もと1あお1あお1そら1お1ひかり1お1つづ2はばた1もど1い1さが1しろ1しろ1くも1つ1ぬ1し1ふ1き1あお1あお1そら1あお1あお1そら1あお1あお1そら]
[00:00.00]ブルーバード - 生物股长 (いきものがかり)
[00:00.44]词：水野良樹
[00:00.62]曲：水野良樹
[00:00.85]飛翔いたら 戻らないと言って
[00:07.32]目指したのは 蒼い 蒼い あの空
[00:25.78]"悲しみ"はまだ覚えられず
[00:29.24]"切なさ"は今つかみはじめた
[00:32.51]あなたへと抱く この感情も
[00:35.62]今"言葉"に変わっていく
[00:38.85]未知なる世界の 遊迷から目覚めて
[00:45.08]この羽根を広げ 飛び立つ
[00:51.38]飛翔いたら 戻らないと言って
[00:57.78]目指したのは 白い 白い あの雲
[01:04.03]突き抜けたら みつかると知って
[01:10.34]振り切るほど 蒼い 蒼い あの空
[01:16.66]蒼い 蒼い あの空
[01:19.76]蒼い 蒼い あの空
[01:29.46]愛想尽きたような音で
[01:32.48]錆びれた古い窓は壊れた
[01:35.62]見飽きたカゴは ほら捨てていく
[01:38.84]振り返ることはもうない
[01:42.01]高鳴る鼓動に 呼吸を共鳴けて
[01:48.33]この窓を蹴って 飛び立つ
[01:54.64]駆け出したら 手にできると言って
[02:00.93]いざなうのは 遠い 遠い あの声
[02:07.25]眩しすぎた あなたの手も握って
[02:13.48]求めるほど 蒼い 蒼い あの空
[02:32.86]墜ちていくと わかっていた
[02:39.26]それでも 光を追い続けていくよ
[02:46.80]飛翔いたら 戻れないと言って
[02:53.04]探したのは 白い 白い あの雲
[02:59.34]突き抜けたら みつかると知って
[03:05.65]振り切るほど 蒼い 蒼い あの空
[03:11.95]蒼い 蒼い あの空
[03:15.06]蒼い 蒼い あの空
```


Except to_srt() function, and to_json(), the library is usable.
