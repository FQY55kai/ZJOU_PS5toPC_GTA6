================================================================================
  GRAND THEFT AUTO VI - PPSA38500 v01.002.001 - BACKPORT FW 9.00 - PS5 PRO (PSSR)
  Duoc tao boi PSVIETHOA.COM - credit: PSVIETHOA.COM
================================================================================

CHI DANH CHO PS5 PRO (FW 10.00 tro len). May thuong / Slim dung ban
..._Grand_Theft_Auto_VI_01.002.001 (khong Pro).

DA SUA GI
  - Goc: ban dump retail 01.002.001 (eboot / libc / libSceNpCppWebApi da giai ma).
    param.json ghi SDK 12.00 nhung ELF that la SDK 7.00 (0x07000038).
  - SDK 9.00 cho eboot, libc, libSceNpCppWebApi;
    param.json 0x1200000000000000 -> 0x0900000000000000.
  - right.sprx la SELF retail that (con ma hoa, SDK 1.00) -> giu nguyen ban goc.
  - eboot: scePadIsRemoteController -> *out = 0.
  - BAT Pro: sceAgcGetIsTrinityMode -> *out = 1. PSSR qua libScePsml_mfsr2 (9/9 ham
    co trong fakelib Psml).
  - fakelib Agc (shim IsTrinityMode = 1) + libScePsml FW 13.60 da va cho 10.01 (bo
    PSSR da chay voi AC Black Flag / 007 tren Pro 10.01); psml_package/KPN9_v070.psp.
  - fakelib ampr_emu (libSceAmpr) kem theo.
  - DLC EMU: 2 nhan PSAL lay tu eboot - 00000000PREORDER (thuong dat truoc),
    0000PROMOTRACKER (khuyen mai). Ca hai CHUA XAC NHAN la nhan so huu that.
    GTAPLUS00001T01M la goi thue bao GTA+ online -> khong khai bao.
    Kem fakelib AppContent / NpEntitlementAccess + dlc_emu.ini o app0.
  - Import strict vs FW 9.00 = 0 ham thieu (fakelib Psml can them 3 ham chi co tu FW 10).
  - CHUA TEST TREN MAY. Neu crash / man den: quay ve ban thuong.
CAI DAT
  Dung ban dump GOC cua game (du lieu giu nguyen). Chep de toan bo noi dung thu
  muc nay vao app0, giu nguyen cau truc thu muc.
  Can loader union-mount (ShadowMount / ShadowMountPlus / BackPork) de fakelib/
  co tac dung. Gui payload backport truoc khi mo game.

CHUNG CHO BAN 9.00
  - SDK tien trinh / module = 9.00 (rieng GT7 = 10.00, Captain Tsubasa 2 ban 7.x = 7.01) (PS5 0x09000040, PS4 0x11590001) cho eboot va
    moi module cua game. param.json: requiredSystemSoftwareVersion va sdkVersion
    = 0x0900000000000000. Chay tren FW 9.00 tro len.
  - Am thanh: SDK >= 8.00 mo cong 12 kenh (7.1.4), khong con ep 7.1.
  - Luu game: SDK >= 6.50 dung duong luu game moi giong ban goc, nen bo cac ban
    va SceSaveDataMount3 / PrepareParam cua ban 4.xx.
  - Chi stub nhung ham FW 9.00 khong co (kiem tra import strict vs 9.00 = 0).
  - CHUA TEST TREN MAY. Neu loi luu game (CE-107098-5 hoac khong tao duoc save),
    bao lai de them ban va luu game.

KIEM TRA
  sha256sum -c SHA256SUMS
