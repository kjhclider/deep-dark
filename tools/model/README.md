# 왕 모델(hoplite) 만들기

지금 chr/hoplite.glb(= chrb/hoplite.wasm)는 Aegis Sentinel(Sketchfab, PixForge, CC BY 4.0)로 만든다. 게임 설정 창 크레딧에 출처를 적었다.
- 원본: https://sketchfab.com/3d-models/aegis-sentinel-ancient-blue-hoplite-warrior-v1-a2619fc3c48a420e9b6fe6091031a401 (glb, 텍스처 4k)
- `blender -b --factory-startup --python aegis_rig.py -- chr/knight.glb aegis.glb hoplite.glb preview.png`
  - aegis.glb는 Sketchfab에서 받은 원본(aegis_sentinel__ancient_blue_hoplite_warrior_v1.glb, 39MB, 저장소 밖 assetschilles\)이다. assetsegis_workegis.glb는 원본이 아니라 완성본 복사본이니 쓰지 않는다(넣으면 한 번 더 돌아가 옆을 보고 걷는다)
  - 오른발 앞코(높이 5% 아래)는 칼에서 뺀다. 높이 40% 아래에서는 몸 뒤로 떨어진 자락(y>0.135)만 망토로 묶는다(종아리, 발뒤꿈치가 망토로 묶이면 걸을 때 신발 옆에 남는다)
  - aegis.glb는 Sketchfab에서 받은 원본(aegis_sentinel__ancient_blue_hoplite_warrior_v1.glb, 39MB, 저장소 밖 assetschilles\)이다. assetsegis_workegis.glb는 원본이 아니라 완성본 복사본이니 쓰지 않는다(넣으면 한 번 더 돌아가 옆을 보고 걷는다)
  - 팔 내린 자세(76도), 벌린 다리(바깥 9도, 오른발 뒤 7도)를 knight 뼈대에 맞춰 묶고 그 자세를 쉼 자세로 둔다(게임은 관절 회전값을 통째로 덮어써서 쉼 자세가 달라도 된다)
  - 칼은 오른손, 방패는 왼쪽 팔뚝에 통째로, 망토는 등뼈와 엉덩이에. 팔과 다리를 잇는 찌꺼기 면은 지운다. 텍스처는 2k로 줄인다
  - 칼과 방패가 모델에 붙어 있어 게임이 쥐여 주는 칼, 방패는 감춘다(makeKing). 옆 폭이 넓어 왕궁, 대전 충돌에 0.25m 여유(kingPad)

예전(임시) 방법: OpenGameArt Achilles(CC0)

원본
- OpenGameArt "Achilles Spartan Greek Warrior" (gamekorp, CC0): https://opengameart.org/content/achilles-spartan-greek-warrior
- Spartan_Achilles.zip 안의 mesh.obj(A자 자세, 뼈대 없음)와 texture.png

순서 (Blender 5.x, 저장소 밖 작업 폴더에서)
1. 피부색: `python skin_fix.py texture.png texture_skin.png` (올리브색 피부를 살색으로)
2. 뼈대 입히기: `blender -b --factory-startup --python rig.py -- chr/knight.glb mesh.obj texture_skin.png hoplite.glb preview.png`
   - knight.glb의 mixamorig 뼈대(T자)를 A자로 굽혀 피부 가중치를 옮기고, A자를 쉼 자세로 둔 임시 뼈대로 팔을 들어 T자로 편 뒤 knight 뼈대에 붙인다
   - 게임은 동작의 관절 회전값을 그대로 옮겨 입히므로 쉼 자세가 knight와 같은 T자여야 한다
3. hoplite.glb를 chr/hoplite.glb와 chrb/hoplite.wasm으로 복사하고 version.json을 다시 계산한다

### 왕 모델 묶기에서 지킬 것 (2026-11-26, 여러 번 틀린 끝에 정한 방식)
- 원본은 assetschillesegis_sentinel__ancient_blue_hoplite_warrior_v1.glb(39MB)다. assetsegis_workegis.glb는 완성본 복사본이라 쓰면 90도 돌아간다.
- 위치로 점마다 가르지 않는다. 이 모델은 망토, 팔, 다리가 모두 한 덩어리로 붙어 있어 위치 기준은 경계에서 늘 어긋났다(발뒤꿈치, 위팔, 손 옆이 번갈아 잘못 묶임).
- 망토는 UV 섬으로 고른다: 몸 뒤쪽 점이 90% 넘는 큰 섬 둘과 거기 맞닿은 가장자리 섬.
- 팔 뼈는 모델 팔에 맞춘다: knight 팔은 옆구리 쪽으로 5~11cm 들어가 있었다. 팔꿈치(위팔 살갗과 팔 보호대 경계, 높이 1.40)와 손목(팔 보호대와 장갑 경계, 1.14)을 텍스처 색으로 재어 옮겼다(ELBOW, WRIST). 팔 점은 위팔, 팔뚝, 손 중 가장 가까운 마디에 다시 묶는다.
- 한 UV 섬이 팔과 몸으로 찢어지지 않게 섬 단위로 맞춘다. 손가락은 손에, 방패를 쥔 왼손은 팔뚝에 통째로.
- 방패도 UV 섬으로 고른다(절반 넘게 방패 상자 안이면 섬 통째로). 상자로만 고르면 테두리가 뜯겨 보였다.
- 팔 쪽 점끼리 이어진 덩어리 중 본체(팔, 손, 칼, 방패)와 떨어진 것(손 옆 허리 가죽 띠, 허리띠 부스러기)은 가까운 몸 점을 따르게 한다. 마지막에 팔 점을 모두 위치대로 다시 묶는다.
- 찌꺼기 면을 지운다: 팔과 다리, 두 팔, 어깨 12cm 아래의 팔과 옆구리, 머리와 등뼈, 망토와 다리, 두 다리를 잇는 면.
- 점(조각)을 지우지 않는다: glTF는 텍스처 이음매마다 점이 갈라져 있어, "작은 조각"은 대부분 진짜 표면이다(지웠더니 방패, 가슴에 구멍이 났다).
- 치마를 엉덩이와 허벅지 섞기로 따로 묶어 보았으나 더 늘어나 되돌렸다.
- 팔에서 몸으로 돌리는 점 중 허리 아래(높이 비율 0.55 아래, LOWBODY)는 망토 공식(Spine, Spine1 섞기)이 아니라 knight에서 팔이 아닌 가장 가까운 점의 가중치를 쓴다. 망토 공식으로 묶었더니 손 옆 치마 자락이 바로 옆 허벅지 점(RightUpLeg 0.96)과 따로 움직였다.
- 허리 아래(높이 비율 0.30~0.56) 가중치는 이웃 점과 고르게 편다(SMOOTH_N 40번). knight 가랑이 경계를 그대로 옮겨 와 치마 조각 안에서 1cm 사이에 왼, 오른 허벅지 몫이 크게 뛰었고, 다리를 벌리면 그 한 변만 늘어나 치마 아랫단이 두 다리 사이에 판처럼 걸렸다.
- 팔꿈치 둘레(관절에서 ELB_R 0.10 안쪽, 위팔과 팔뚝에만 묶인 점)도 같은 방식으로 편다(ELB_N 30번). 가까운 마디로 나눠 묶은 경계에서 1~2cm 사이에 팔뚝 1.00 → 위팔 0.77로 뛰었다. 범위 0.07로는 팔꿈치 뒤쪽 점(관절에서 14cm)에 닿지 않았다.
- 가중치를 펼 때 지킬 것: 팔, 손, 칼, 방패, 망토 점은 바꾸지도 이웃으로 쓰지도 않는다(팔 몫이 0.01만 있어도 뺀다). 이음매의 같은 자리 점은 펼 대상끼리만 잇는다. 팔 점과 같은 자리라고 함께 평균 내었더니 0.50/0.50 점이 생겨 팔 쪽이 오히려 나빠졌다.
- 확인은 게임 안에서 실제 동작으로 한다: 동작 중에 원래보다 2.5배, 6cm 넘게 늘어나는 변을 뼈 쌍별로 세고(sw_slash1 0.2/0.35/0.5, sw_slash3 0.4, sw_attack2 0.45, sw_walk 0.3, sw_idle2 0.3), 여러 각도로 그려 본다. Blender에서 뼈를 임의로 돌린 미리보기는 실제 동작과 달라 믿지 않는다. 새 glb는 게임 탭에서 GLTFLoader로 읽어 CHR.gltf.hoplite만 바꿔 끼우면 파일을 덮어쓰지 않고 잴 수 있다.
- 남은 것(2026-11-26, 7장면 합계, 같은 변이 여러 장면에 나오면 장면마다 셈): 늘어난 변 2,418 → 172, 그중 팔, 손이 들어간 쌍 268 → 93. 남은 것은 망토 아래 어깨 뒤쪽(RightArm~Spine2 58, 망토에 가려 겉에서 거의 안 보임), 목 뒤(Head~Neck 24), 어깨 앞 가슴(Spine2~Spine2 24), 왼 무릎(LeftLeg~LeftUpLeg 21).

# 바르고스 모델(vargoth) 만들기

chr/vargoth.glb(= chrb/vargoth.wasm)는 Sketchfab "Corrupted King in Black Armor with Bone Crown"(Pigcraft/s8819296, CC BY, AI로 만든 한 덩어리 메시)로 만든다.
- 원본: assets\corrupted_king_in_black_armor_with_bone_crown.glb(135MB, 200만 면). assets\vargoth_work\vg_dec.glb(6MB)는 vg_prep.py가 만든 중간본(6만 면, 정면 -Y로 돌림), vargoth_work\vargoth.glb는 예전 완성본 복사본이니 입력으로 쓰지 않는다.
1. `blender -b --python vg_prep.py -- corrupted_king....glb vg_dec.glb grid.png 60000`
2. `blender -b --factory-startup --python vg_rig.py -- chr/knight.glb vg_dec.glb vargoth.glb preview.png`
3. vargoth.glb를 chr/vargoth.glb와 chrb/vargoth.wasm으로 복사한다. 게임은 makeHero("vargoth")로 만들고(처음 화면, 프롤로그, 망자의 왕좌 전투) 칼은 모델에 붙은 것을 쓴다.

### 바르고스 묶기에서 지킬 것 (2026-11-26)
- 이 모델은 텍스처 이음매마다 점이 갈라져 UV 섬 하나가 곧 따로 떨어진 조각이다(섬 830개). 칼, 망토, 깃은 섬 통째로 고른다.
- 망토: 점 80%가 몸 뒤(y>0.085, 어깨 사이 등은 y>0.04, 다리 옆 자락은 |x|>0.24)인 섬, 그리고 망토에 맞닿고 점 60%가 뒤쪽인 섬으로 넓힌다. 넓히지 않으면 등 위쪽, 팔 뒤 망토 조각이 팔에 묶여 팔을 들 때 망토에 구멍이 났다. 어깨 갑옷(높이 72% 위, |x|>0.11)은 넓히는 데서 뺀다.
- 칼: 칼날 상자에 더해 오른손 뒤 위로 나온 칼자루 끝(금색 고리)을 따로 고른다. 빠지면 허벅지에 묶여 손과 따로 떠다닌다.
- 높은 깃은 머리가 아니라 가슴, 목(Spine2 0.6, Neck 0.4)에. 머리에 묶이면 머리와 가슴 사이가 가장 많이 늘어났다(339면).
- knight 팔꿈치는 모델 팔보다 약 9cm 안쪽이었다. 팔꿈치(팔 보호대 윗단 바로 아래, 높이 0.665), 손목(보호대와 장갑 경계, 0.515)을 정면, 옆 그림에 격자를 대고 재어 옮겼다(ELBOW, WRIST).
- 팔 보호대가 두꺼워 팔뚝 안쪽 면이 팔 중심선에서 11cm까지 떨어져 있다. 팔뚝 마디는 FA_IN(0.058 키)까지, 섬은 절반 넘게 팔이고 중심이 팔 가까이면 통째로 팔에 묶는다(팔뚝 앞 조각이 몸에 남아 15cm 떨어졌다).
- 팔에서 떼어 몸으로 돌리는 옆구리 점은 높이로 정한 등뼈 가중치가 아니라 가장 가까운 몸 점의 가중치를 따른다.
- 확인: 게임 탭에서 GLTFLoader로 읽어 CHR.gltf.vargoth만 바꿔 끼우고, 칼 동작 9개, 걷기 2, 달리기, 대기 4, 주먹 들기, 기 모으기 각 7장면에서 늘어나는 면을 센다. 섬마다 주변 표면과의 거리가 동작 중 얼마나 벌어지는지 재면 떠다니는 조각이 바로 나온다. 텍스처 색으로 금색 섬을 골라 묶인 뼈를 보면 칼자루처럼 엉뚱한 뼈에 묶인 장식을 찾기 쉽다.
- 결과(2026-11-26): 늘어난 면 2,209 → 772, 동작 중 5cm 넘게 떨어지는 조각 15cm → 최대 5.5cm. 남은 것은 sw_slash1, sw_slash2의 큰 허리 비틀기에서 엉덩이와 배(Hips~Spine 144), 허벅지 안(UpLeg 같은 뼈 안 167), 발목(Foot~Leg 107). 모두 knight에서 옮긴 가중치 경계라 왕 모델처럼 허리 아래 가중치를 고르게 펴면 더 줄일 수 있다.

# 선왕 모델(oldking) 만들기

chr/oldking.glb(= chrb/oldking.wasm)는 Sketchfab "Old king armor"(Pedro B. Goulart, CC BY 4.0, 면 4만, 금테 판금 갑옷)로 만든다. 프롤로그 "선왕의 마지막 밤"에서 왕(makeKing의 S.prologue 갈래)이 이 모델을 쓴다.
- 원본: 저장소 밖 assets\old_king_armor.glb(50MB, 텍스처 4k 셋). 작업 파일은 assets\oldking_work\
- `blender -b --factory-startup --python oldking_rig.py -- chr/knight.glb old_king_armor.glb oldking.glb preview.png`
- oldking.glb를 chr/oldking.glb와 chrb/oldking.wasm으로 복사한다(2.9MB, 색 텍스처 2k, 금속, 거칠기와 노멀 1k).

### 선왕 묶기에서 지킬 것 (2026-11-26)
- 이 모델은 AI로 만든 한 덩어리가 아니라 작가가 뼈대(Hip, Belly, Torax, Clavicule, Arm, Forearm, Hand, 손가락, Femur, Shin, Feet, FeetTip, 어깨, 팔꿈치, 무릎 보호대 뼈)와 가중치를 칠한 모델이다. 그래서 왕, 바르고스처럼 knight 몸에서 가중치를 옮기지 않고(UV 섬 고르기, 팔 다시 묶기, 찌꺼기 면 지우기가 필요 없다) 원본 가중치를 mixamo 이름으로 바꿔 쓴다. 보호대 뼈는 붙은 마디로(어깨 → Shoulder, 팔꿈치 → ForeArm, 무릎 → Leg), Belly는 높이로 Spine, Spine1에 나눈다.
- 원본 파일은 걷는 듯한 자세로 저장되어 있다. 포즈를 지워 쉼 자세(두 발을 모으고 팔을 약 72도 내린 대칭 자세)로 묶는다. 위가 +Y, 앞이 +Z라 X축으로 90도 돌린다.
- knight 뼈는 팔다리(위팔, 팔뚝, 손, 손가락, 허벅지, 정강이, 발)만 모델 뼈 방향으로 돌리고, 쇄골, 등뼈, 목은 knight 방향 그대로 둔다. 그다음 모든 관절 자리를 모델 관절로 옮긴다(방향과 비틀림은 그대로 통째로 옮김). 쇄골까지 모델 방향(가슴 가운데 앞에서 뒤로 28도)으로 돌렸더니, 게임 동작이 쇄골 회전을 knight 값으로 덮어써 대기 자세에서도 팔이 통째로 돌아 팔과 가슴 사이가 늘어났다(Arm~Spine2 1,200).
- 원본 가중치는 엉덩이 뒤(엉덩이~허벅지)와 어깨뼈 아래(가슴~위팔)에서 1~2cm 사이에 1.0 → 0.4로 바뀐다. 원본 뼈대보다 크게 움직이는 게임 동작에서 그 짧은 변이 7~14cm로 늘어났다. 엉덩이, 등뼈, 목, 쇄골, 위팔, 허벅지에만 묶인 점끼리 이웃과 고르게 편다(SMOOTH_N 20번, 이음매의 같은 자리 점은 한 점으로).
- 무기가 모델에 없다. 게임이 쥐여 주는 칼, 방패를 그대로 쓴다(helmet 표시를 켜지 않는다, 갑주 장식 heroDeco도 더하지 않는다).
- 결과(2026-11-26, 게임 탭에서 2.5배 그리고 6cm 넘게 늘어난 변, 같은 변을 장면마다 셈): 7장면(sw_slash1 0.2/0.35/0.5, sw_slash3 0.4, sw_attack2 0.45, sw_walk 0.3, sw_idle2 0.3) 1,879 → 30. 칼 동작 전부, 걷기, 달리기, 대기, 주먹 들기 등 20개 x 4장면 323(같은 셈법으로 지금 왕 모델 hoplite는 4,863). 남은 것은 팔을 크게 들 때 겨드랑이(Arm~Spine2, Arm 같은 뼈 안)와 무릎 보호대(Leg~UpLeg).
