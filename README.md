# simple blog 説明

## 概要

- simple blogは旧来のサーバーサイドレンダリングを行う基本的なWebアプリケーションの学習としてDjangoを用いて作成した記事投稿機能やユーザフォロー機能などを持つ簡易的なブログサービスです。
- simple blogはAWS上にデプロイされており、<https://www.simpleblogks.tk>からアクセスして実行する事が可能です。セキュリティ対策としてBasic認証を設定しておりますので、メールまたはメッセージに記載したユーザ名とパスワードを入力して下さい。
  - 夜間・早朝はサーバを停止しており 10:00 ~ 20:00 の間にサーバを稼働しております。ご了承下さい。

## ER図

![ER](https://user-images.githubusercontent.com/80889322/137302326-f1bd095f-a89d-4e05-bd68-ec919264489a.png)

## ネットワーク構成図

- simple blogはAWS上にALB・EC2・RDS・S3を利用した基本的なネットワーク上にデプロイしております。
- AWS無料利用枠を利用しているためEC2インスタンスタイプはt2.microを利用しておりますので、処理が遅い可能性があります。ご了承下さい。

![AWSNetwork](https://user-images.githubusercontent.com/80889322/137302321-48dcc0ce-5efa-4763-9923-484310469730.png)

## アプリケーションイメージ図

- WebサーバとアプリケーションサーバはEC2インスタンス上のDockerコンテナとして稼働しています

![AppStructure](https://user-images.githubusercontent.com/80889322/137302318-9005deb3-bd00-4777-832e-748288764881.png)

## 利用しているライブラリ

### バックエンド

- django
- pillow
- django-environ
- django-axes
- boto3
- django-storages
- gunicron
- mysqlclient

### フロントエンド

- jQuery
  - お気に入り機能とフォロー機能を非同期に行うために利用しております。

## 認証に関する機能

### 登録

- register を選択し、ユーザ名・メールアドレス・パスワード・確認用のパスワードを入力する事でユーザ登録を行う事が可能です。

![register](https://user-images.githubusercontent.com/80889322/137301307-c3d668d8-2602-4ac2-8530-10792e95eb60.gif)

### ログイン

- ログインしていない状態で login を選択し、正しいユーザ名・パスワードを入力する事でログインを行う事が可能です。
- ログインの認証に3回失敗するとdjango-axesによって、そのアカウントをロックする様にしております。

![login](https://user-images.githubusercontent.com/80889322/137301271-693d8097-d596-4591-ae4e-b89c96407531.gif)

### ログアウト

- ログインしている状態で logout を選択する事で、ログアウトを行う事が可能です。

<img width="1440" alt="logout" src="https://user-images.githubusercontent.com/80889322/137301303-fb8ec157-5828-4870-84d7-8a9de22a3eb1.png">

## 記事一覧ページに関する機能

- 記事一覧ページには simple blog を選択する事でアクセスする事が可能です。

### タグによる記事検索

- タグ選択フォームから任意のタグを指定して 検索 を選択する事で、指定したタグを持つ記事のみを検索する事が可能です。

![tag_search](https://user-images.githubusercontent.com/80889322/137301077-3b3d5989-f058-4717-a6f6-3b20d8763586.gif)

### 単語名による記事検索

- 入力フォームに任意の文字列を指定して 検索 を選択する事で、指定した文字列をタイトルまたは記事内に持つ記事のみを検索する事が可能です。

![word_search](https://user-images.githubusercontent.com/80889322/137301085-ba7b7865-0d55-4fc6-af04-6e0579cacf85.gif)

### タグ・単語名による記事検索

- タグと文字列のどちらも利用した検索を行う事で、指定したタグを持つ記事の中から指定した文字列をタイトルまたは記事内に持つ記事のみを検索する事が可能です。

![tag_word_search](https://user-images.githubusercontent.com/80889322/137301081-e114e9d3-d176-46c5-b4ef-c34e77dd4661.gif)

### ページネーション

- 記事一覧ページ下部にあるボタンから次の5個の記事を取得する事が可能です。

![pagination](https://user-images.githubusercontent.com/80889322/137301063-14367205-ad89-482e-8f9b-e81dc8919bc8.gif)

## 記事ページに関する機能

- 記事ページには記事一覧ページから、その記事のタイトルを選択する事などでアクセスする事が可能です。

### 記事のお気に入りとお気に入り解除

- ログインしている状態で お気に入りに追加 を選択する事でお気に入りに追加する事が可能です。
- また、ログインしている状態かつ既にお気に入りに追加している場合は お気に入り済み を選択する事でお気に入りから削除する事が可能です。

![favorite](https://user-images.githubusercontent.com/80889322/137299624-81f2c8d0-35ae-441c-8315-8c350727c50c.gif)

### コメント投稿

- ログインしている状態でコメント入力フォームにコメントを入力して コメントを投稿 を選択する事で、その記事に対するコメントを投稿する事が可能です。

![comment](https://user-images.githubusercontent.com/80889322/137299603-c84bd40d-8397-458d-806a-bd28475157b1.gif)

### 指定したタグを持つ記事の検索

- Tagsに表示されているタグを選択する事で、そのタグを持つ記事の検索結果を取得する事が可能です。

![tag](https://user-images.githubusercontent.com/80889322/137299626-b921e24c-ecf1-4b37-b76b-e962eac9ee02.gif)

## ユーザページに関する機能

- ユーザページには記事一覧ページから、その記事の作者名を選択する事などでアクセスする事が可能です。

### 投稿記事一覧

- 投稿記事一覧ではそのユーザが投稿した記事の一覧が表示されており、任意の記事タイトルを選択する事で指定した記事ページへアクセスする事が可能です。

![articles](https://user-images.githubusercontent.com/80889322/137301885-44e39f2a-e5ee-430b-aeff-3274b756db59.gif)

### お気に入り記事一覧

- 投稿記事一覧ではそのユーザがお気に入りに追加した記事の一覧が表示されており、任意の記事タイトルを選択する事で指定した記事ページへアクセスする事が可能です。

![favorites](https://user-images.githubusercontent.com/80889322/137301909-adadbfc8-c58a-41a2-89ed-bf3ae895c7a7.gif)

### フォロー機能

- ログインしている状態でプロフィール部分の フォローする を選択する事が可能です。
- また、ログインしている状態かつ既にそのユーザをフォローしている場合は フォロー中 を選択する事でフォロー解除を行う事が可能です。

![follow](https://user-images.githubusercontent.com/80889322/137301913-82880fb2-b79e-400e-9c29-35f2ab55b457.gif)

### フォローユーザ一覧

- フォローユーザ一覧ではそのユーザがフォローしているユーザが表示されており、ユーザ名を選択する事で指定したユーザのユーザページへアクセスする事が可能です。
- また、ログインしている状態ではフォローユーザ一覧において、指定したユーザのフォローとフォロー解除を行う事が可能です。

![follows](https://user-images.githubusercontent.com/80889322/137301920-48f6a369-edd3-4ab0-a0dc-c9f8c1d2990a.gif)

### フォロワーユーザ一覧

- フォロワーユーザ一覧ではそのユーザをフォローしているユーザが表示されており、ユーザ名を選択する事で指定したユーザのユーザページへアクセスする事が可能です。
- また、ログインしている状態ではフォロワーユーザ一覧において、指定したユーザのフォローとフォロー解除を行う事が可能です。

![followers](https://user-images.githubusercontent.com/80889322/137301917-8d943dae-1410-4890-a84a-9b9aa296878f.gif)

## 設定ページに関する機能

- 設定ページにはログインしている状態で settings を選択する事でアクセスする事が可能です。

### ユーザ名変更

- 入力フォームに任意のユーザ名を入力して 更新 を選択する事で、ユーザ名を更新する事が可能です。

![changename](https://user-images.githubusercontent.com/80889322/137301390-d13745c7-edaa-4c53-8e19-15a70b38e796.gif)

### メールアドレス変更

- 入力フォームに任意のメールアドレスを入力して 更新 を選択する事で、メールアドレスを更新する事が可能です。

![changeemail](https://user-images.githubusercontent.com/80889322/137301366-0d41219a-8ff5-448e-8874-dac6661bd7e8.gif)

### パスワード変更

- 入力フォームに現在のパスワード・新しいパスワード・確認用のパスワードを入力して 更新 を選択する事で、パスワードを更新する事が可能です。

![changepassword](https://user-images.githubusercontent.com/80889322/137301393-525e66bd-5d34-4a05-b6a2-c3927fa46abc.gif)

### プロフィール変更

- ファイルを選択 からアイコン画像をアップロードし、入力フォームにプロフィールメッセージを入力して 更新 を選択する事で、アイコン画像とプロフィールメッセージを更新する事が可能です。

![changeprofile](https://user-images.githubusercontent.com/80889322/137301397-aa8014d6-3cdb-4219-b22b-56342d03d404.gif)

### フォローユーザ一覧

- フォローユーザ一覧では自分がフォローしているユーザが表示されており、ユーザ名を選択する事で指定したユーザのユーザページへアクセスする事が可能です。
- また、指定したユーザのフォローとフォロー解除を行う事が可能です。

![follow](https://user-images.githubusercontent.com/80889322/137301408-ec1bb2fe-7fd5-43b0-bd18-6289bde38e6f.gif)

### フォロワーユーザ一覧

- フォロワーユーザ一覧では自分をフォローしているユーザが表示されており、ユーザ名を選択する事で指定したユーザのユーザページへアクセスする事が可能です。
- また、指定したユーザのフォローとフォロー解除を行う事が可能です。

![follower](https://user-images.githubusercontent.com/80889322/137301411-f06f2853-8948-4760-80b1-3b3e86aaabb9.gif)

### 記事作成機能

- 入力フォームに任意のタイトルと本文を入力し、任意カテゴリタグを指定する事で新規記事を作成する事が可能です。

![createarticle](https://user-images.githubusercontent.com/80889322/137301401-9af1f0b3-9186-40e1-8f76-43f210821227.gif)

### 記事編集機能

- 記事の編集 から自分が投稿した記事の一覧を取得する事が可能であり、任意の記事を指定する事で、その記事の編集ページへアクセスする事が可能です。
- 記事編集ページではタイトル・本文・カテゴリタグを現在の内容から新しい内容へ更新する事が可能です。
- また、記事の削除を記事編集ページの下部の 削除 を選択する事で削除する事が可能です。　

![updatedeleteartcile](https://user-images.githubusercontent.com/80889322/137301412-b0cbeb12-540e-4581-b71c-0d913c25b77c.gif)

### ユーザ削除機能

- ユーザの削除 を選択し、確認画面で 削除 を選択する事で現在ログインしているアカウントを削除する事が可能です。

![deleteuser](https://user-images.githubusercontent.com/80889322/137301404-6594a7e3-a539-4d2a-afee-27676ff9fdd2.gif)

## 備考

- 管理ツールへのアクセスはnginxの設定ファイルでIPアドレスによるアクセス制限を行っております。