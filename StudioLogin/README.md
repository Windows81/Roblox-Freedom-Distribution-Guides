## How to find the patch?

## Background

I found a version of Studio from late 2021 ([v493.1.15175](https://archive.org/details/roblox-version-1fca050e38094184)) with a patch applied in x86 such that no login screen would be required. There was a change from `jnz` to `jz` at file address `0x002B951C`. This patch was location near a unique string reference to `"Studio.App.AutoSaveDialog.OpenRobloxFile"`. The specific fix that Reggie applied, however, can't be reproduced in my target versions of v347 and v463. However, a very similar one has been confirmed to work in v463.

When you launch v463 Studio without command-line arguments, you are presented with a login screen.

![](image.png)

You may be tempted to try _bypassing_ this through several methods:

1. **Ctrl + O:** a similar message shows up: `"You must log in to open files."`

2. **Dragging to Topbar:** in 2021, the login screen could be bypassed by dragging the desired file from File Explorer to the top of the Studio window. This option does not work in late-2025 versions of Studio.

3. **Ctrl + N:** Rōblox has had this action accounted for since at latest 2018. An error string `"You must log in to create new files."` shows up. Let's investigate this option further with x64dbg.

---

**At the end, I've needed to perform two separate patches.**

## (1) Patching `LoggedInUser::getIsLoggedIn`

To bypass the login page in the first place, I've needed to patch a partciular function to always return `true`.

### Finding Strings to Locate

![](image-1.png)

In the `RobloxStudioBeta.exe` v463 executable, there are no results (via x64dbg) for the string `"You must log in to create new files."`

This is because Rōblox stores most user-facing strings in a localisation table.

You will find that desired string in the Rōblox Client Tracker data at [`./QtResources/Translation/StudioStringsUntranslated.csv`](https://github.com/MaximumADHD/Roblox-Client-Tracker/blob/f867742be117235b24b2be7500eada1d20ba42f3/QtResources/Translation/StudioStringsUntranslated.csv#L789). The translation-agnostic key is **`"Studio.App.MainWindow.LogInToCreateNewFiles"`**.

The CSV data was compressed as a Qt resource; the Client Tracker used the [qtextract](https://github.com/axstin/qtextract.git) tool to extract the CSV data.

I search for string references in user modules in `RobloxStudioBeta.exe` v463 executable (using x64dbg) for `"Studio.App.MainWindow.LogInToCreateNewFiles"`. One result shows up at address `000000014026CD15`.

I add a breakpoint right there at `000000014026CD15`. I make sure that Studio is at the starting login screen and hit Ctrl + N again. The breakpoint is hit.

### Analysing Branch Logic in Nearby Calls

I step over the execution trace and notice that the message box shows up during a call to `robloxstudiobeta.140266D90`. This call is the first instruction after the breakpoint to use opcode `E8` and is located at `000000014026CD59`: some 12 instructions after the breakpoint.

The routine we're calling begins at `0000000140266D90` and ends at `0000000140266FA1`. Judging by the `mov al, 0x1` near the end of the snippet below, we can infer that it returns a boolean.

---

```
0000000140266DBF | 4C:8B00                  | mov     r8, qword ptr ds:[rax]          |
0000000140266DC2 | 48:8BC8                  | mov     rcx, rax                        |
0000000140266DC5 | 41:FF90 80000000         | call    qword ptr ds:[r8 + 0x80]        | {C}
0000000140266DCC | 803D 6512E802 00         | cmp     byte ptr ds:[0x1430E8038], 0x0  |
0000000140266DD3 | 0F84 02010000            | je      robloxstudiobeta.140266EDB      | {B1}
0000000140266DD9 | 84C0                     | test    al, al                          |
...
0000000140266ED4 | E8 07769201              | call    <robloxstudiobeta.rbxDeallocate |
0000000140266ED9 | EB 08                    | jmp     robloxstudiobeta.140266EE3      |
0000000140266EDB | 84C0                     | test    al, al                          | {B2}
0000000140266EDD | 0F85 AC000000            | jne     robloxstudiobeta.140266F8F      | {A1}
0000000140266EE3 | 0FB60D DEEDEC02          | movzx   ecx, byte ptr ds:[0x143135CC8]  |
0000000140266EEA | 84C9                     | test    cl, cl                          |
0000000140266EEC | 74 0F                    | je      robloxstudiobeta.140266EFD      |
0000000140266EEE | 4C:8BC3                  | mov     r8, rbx                         |
0000000140266EF1 | 48:8D15 60461F02         | lea     rdx, qword ptr ds:[0x14245B558] | 000000014245B558:"[FLog::Always] %s"
0000000140266EF8 | E8 E3AB9201              | call    robloxstudiobeta.141B91AE0      |
0000000140266EFD | 48:8BD3                  | mov     rdx, rbx                        |
0000000140266F00 | 48:8D8C24 A8000000       | lea     rcx, qword ptr ss:[rsp + 0xA8]  |
0000000140266F08 | FF15 CAF3E501            | call    qword ptr ds:[<public: __cdecl  |
0000000140266F0E | 90                       | nop                                     |
0000000140266F0F | C74424 20 FFFFFFFF       | mov     dword ptr ss:[rsp + 0x20], 0xFF |
0000000140266F17 | 45:33C9                  | xor     r9d, r9d                        |
0000000140266F1A | 4C:8D05 0F211E02         | lea     r8, qword ptr ds:[0x142449030]  | 0000000142449030:"Studio.App.MainWindow.RobloxStudio"
0000000140266F21 | 48:8D9424 A0000000       | lea     rdx, qword ptr ss:[rsp + 0xA0]  |
0000000140266F29 | 48:8D0D 685F2102         | lea     rcx, qword ptr ds:[0x14247CE98] |
0000000140266F30 | FF15 AAF9E501            | call    qword ptr ds:[<public: class QS |
0000000140266F36 | 90                       | nop                                     |
0000000140266F37 | C74424 20 00000000       | mov     dword ptr ss:[rsp + 0x20], 0x0  |
0000000140266F3F | 41:B9 00040000           | mov     r9d, 0x400                      |
0000000140266F45 | 4C:8D8424 A8000000       | lea     r8, qword ptr ss:[rsp + 0xA8]   |
0000000140266F4D | 48:8D9424 A0000000       | lea     rdx, qword ptr ss:[rsp + 0xA0]  |
0000000140266F55 | 48:8BCF                  | mov     rcx, rdi                        |
0000000140266F58 | FF15 526BE601            | call    qword ptr ds:[<public: static e |
0000000140266F5E | 90                       | nop                                     |
0000000140266F5F | 48:8D8C24 A0000000       | lea     rcx, qword ptr ss:[rsp + 0xA0]  |
0000000140266F67 | FF15 C3F3E501            | call    qword ptr ds:[<public: __cdecl  |
0000000140266F6D | 90                       | nop                                     |
0000000140266F6E | 48:8D8C24 A8000000       | lea     rcx, qword ptr ss:[rsp + 0xA8]  |
0000000140266F76 | FF15 B4F3E501            | call    qword ptr ds:[<public: __cdecl  |
0000000140266F7C | 32C0                     | xor     al, al                          |
0000000140266F7E | 48:8B9C24 90000000       | mov     rbx, qword ptr ss:[rsp + 0x90]  |
0000000140266F86 | 48:81C4 80000000         | add     rsp, 0x80                       |
0000000140266F8D | 5F                       | pop     rdi                             |
0000000140266F8E | C3                       | ret                                     |
0000000140266F8F | B0 01                    | mov     al, 0x1                         | {A2}
0000000140266F91 | 48:8B9C24 90000000       | mov     rbx, qword ptr ss:[rsp + 0x90]  |
0000000140266F99 | 48:81C4 80000000         | add     rsp, 0x80                       |
0000000140266FA0 | 5F                       | pop     rdi                             |
0000000140266FA1 | C3                       | ret                                     |
```

To reach the branch which returns with `1`, we need to ensure that `al` is also `1` when the EIP is at `0000000140266EDB`. This is evident by how the statement I notated as `{A1}` can jump directly to `{A2}`. We know that this is the only way to reach this branch because:

1. An unconditional `jmp` instruction is placed in the statement prior to `{B2}`.
2. The statement prior to `{A2}` is a `ret` instruction, effectively serving as a jump.

Owing to the `jmp` statement per (1), we know that `al` comes from some other place, that being before `{B1}`, which is a jump for an unrelated condition. The `al` originates from the result of a function call at `{C}`.

To determine the exact address of this call, we need to add another breakpoint. We do the same test as before to get this breakpoint captured. Once hit, _step into_ that function. In v463, that destination function begins at `00000001405F2100`.

### Final Patch

We apply the following patch to ensure that the function always returns a truish vaue.

```patch
-00000001405F2100 | 0FB641 48                | movzx   eax, byte ptr ds:[rcx + 0x48]   | rcx+48:AmdPowerXpressRequestHighPerformance+1C083C
+00000001405F2100 | 0C FF                    | or      al, 0xFF                        |
+00000001405F2102 | 90                       | nop                                     |
+00000001405F2103 | 90                       | nop                                     |
 00000001405F2104 | C3                       | ret                                     |
```

### Confirmation via the v548 PDBs

Using IDA, and looking through the v548 PDB files (which some Rōblox reverse-engineers refer to for research), we can confirm our findings.

To begin, the string `"Studio.App.MainWindow.LogInToCreateNewFiles"` appears exactly once, that being in `RobloxMainWindow::fileNew`.

We can use IDA to decompile the referring code:

```cpp
void __fastcall RobloxMainWindow::fileNew(RobloxMainWindow *this)
{
  ...
  QMetaObject::tr(
    &RobloxMainWindow::staticMetaObject,
    (const char *)&v16,
    "Studio.App.MainWindow.LogInToCreateNewFiles",
    0);
  v2 = QString::toStdString(&v16, ptr);
  if ( *(_QWORD *)(v2 + 24) >= 0x10u )
    v2 = *(_QWORD *)v2;
  v3 = !RobloxMainWindow::checkLoggedInAndDisplayError(this, (const char *)v2);
  if ( v15 >= 0x10 )
  {
    v4 = ptr[0];
    if ( v15 + 1 >= 0x1000 )
    {
      v4 = *((void **)ptr[0] - 1);
      if ( (unsigned __int64)((char *)ptr[0] - (char *)v4 - 8) > 0x1F )
        _invalid_parameter_noinfo_noreturn();
    }
    operator delete(v4);
  }
  ...
```

Importantly, this snippet refers to method `RobloxMainWindow::checkLoggedInAndDisplayError`:

```cpp
char __fastcall RobloxMainWindow::checkLoggedInAndDisplayError(RobloxMainWindow *this, const char *errorMessage)
{
  ILoginManager *loginManager; // rax
  LoggedInUser *loggedInUser; // rax
  QTypedArrayData<unsigned short> *errorMessageArray; // rbx
  char v8; // [rsp+50h] [rbp+18h] BYREF
  char v9; // [rsp+58h] [rbp+20h] BYREF

  loginManager = SingletonInterfaceFetcher::getInterface<ILoginManager>();
  loggedInUser = (LoggedInUser *)loginManager->DEPRECATED_getLoggedInUser(loginManager);
  if ( loggedInUser->getIsLoggedIn(loggedInUser) )
    return 1;
  if ( FLog::Always )
    FLog::FastLogS(FLog::Always, "[FLog::Always] %s", errorMessage);
  errorMessageArray = QString::fromUtf8(&v9, (_DWORD)errorMessage).d;
  QMetaObject::tr(&RobloxMainWindow::staticMetaObject, &v8, "Studio.App.MainWindow.RobloxStudio", 0);
  QMessageBox::critical(this, &v8, errorMessageArray, 1024, 0);
  QString::~QString(&v8);
  QString::~QString(&v9);
  return 0;
}
```

The interesting function in the snippet above is `getIsLoggedIn`. Upon searching for function named `getIsLoggedIn`, we find:

```cpp
bool __fastcall LoggedInUser::getIsLoggedIn(LoggedInUser *this)
{
  return this->m_isLoggedIn && !this->m_isLoggingOut;
}
```

This function, as short as it looks, is where the patch takes place.

## (2) Firing `ILoginManager::loginSuccess`

**This patch only applies to RFD's v463 Studio binary so far.** This is because v347 use Qt4, which recommends different signal-slot syntax. It appears that the patch is not necessary in RFD's v347 binary.

For more information on how slots and signals work for the end user, refer to [some AI-slop explanation that I found online](https://runebook.dev/en/docs/qt/qobject/connect-3).

Upon normal conditions, Studio calls a function when a user is successfully authenticated, which other modules in Studio can use (through Qt5) to handle callbacks. That function is named `ILoginManager::loginSuccess`.

The goal is to call `ILoginManager::loginSuccess` exactly once when Rōblox Studio is initialising. From my understanding, only the first argument needs to be populated.

_I think, guessing and extrapolating from the v548 PDB symbols,_ that this is how Rōblox's engineers actually make Studio handle callbacks on authentication:

```cpp
loginSuccessVTable.__vftable = (QObject_vtbl *)ILoginManager::loginSuccess;
QObject::connect(
  anySenderObject, // SENDER: can be any object
  &ILoginManager::loginSuccess,  // SIGNAL: the signal function
  LoginManager::Instance(), // RECEIVER: studio treats LoginManager as a global singleton object
  &anySlotFunction // SLOT: can be any function
);
```

Note that in callbacks `ILoginManager::loginSuccess` has its address read directly onto memory using the `lea` assembly instruction.

### To Find in Other Studio Builds

The function `ILoginManager::loginSuccess`

Analysing the v548 debug symbols, searching in IDA for `ILoginManager::loginSuccess` gave me multiple candidates to find this function in other versions. The best candidate is `LoginManager::initialize` for its proximity to plenty of unique strings:

- `"DEPRECATED_getLoggedInUser()"` (or simply `"getLoggedInUser()"` in v463),
- `"getConversationProxyModel()"`,
- `"getTemplatePageProxyModel()"`,
- `"qrc:/StartPage/StartPageMain.qml"`,
- etc.

The following is nearby code generated by IDA, surrounding the `ILoginManager::loginSuccess` reference:

```cpp
v21 = QMetaObject::indexOfMethod(&TemplatePageController::staticMetaObject, "getTemplatePageProxyModel()");
QMetaObject::method(&TemplatePageController::staticMetaObject, &v73, v21);
v22 = QMetaMethod::typeName(&v73);
v23 = QByteArray::QByteArray(&v60, v22, -1);
v24 = QByteArray::replace(v23, "*", pass);
v25 = QByteArray::constData(v24);
qmlRegisterInterface<TemplatePageProxyModel>(v25);
QByteArray::~QByteArray(&v60);
v26 = QMetaObject::indexOfMethod(&ShareModalController::staticMetaObject, "getConversationProxyModel()");
QMetaObject::method(&ShareModalController::staticMetaObject, &v74, v26);
v27 = QMetaMethod::typeName(&v74);
v28 = QByteArray::QByteArray(&v61, v27, -1);
v29 = QByteArray::replace(v28, "*", pass);
v30 = QByteArray::constData(v29);
qmlRegisterInterface<ConversationProxyModel>(v30);
QByteArray::~QByteArray(&v61);
v31 = QMetaObject::indexOfMethod(&LoginManager::staticMetaObject, "DEPRECATED_getLoggedInUser()");
QMetaObject::method(&LoginManager::staticMetaObject, &v75, v31);
v32 = QMetaMethod::typeName(&v75);
v33 = QByteArray::QByteArray(&v62, v32, -1);
v34 = QByteArray::replace(v33, "*", pass);
v35 = QByteArray::constData(v34);
qmlRegisterInterface<DEPRECATED_ILoggedInUser>(v35);
QByteArray::~QByteArray(&v62);
v36 = MRULocalFileStore::Instance();
MRULocalFileStore::connectToLoginManagerQSignals(v36, this);
v79 = LoginManager::initializeStartPage;
loginSuccessVTable.__vftable = (QObject_vtbl *)ILoginManager::loginSuccess;
v37 = (QObject_vtbl *)operator new(0x18u);
v55.__vftable = v37;
if ( v37 )
{
  v38 = v79;
  LODWORD(v37->metaObject) = 1;
  v37->qt_metacast = (void *(__fastcall *)(QObject *, const char *))QtPrivate::QSlotObject<void (RobloxQQuickViewContainer::*)(void),QtPrivate::List<>,void>::impl;
  v37->qt_metacall = (int (__fastcall *)(QObject *, QMetaObject::Call, int, void **))v38;
}
else
{
  LODWORD(v37) = 0;
}
```

Note the key statement:

```cpp
loginSuccessVTable.__vftable = (QObject_vtbl *)ILoginManager::loginSuccess;
```

Observing this code snippet, I notice that:

- The nearest string to the reference statement is _up_;
  - **Begin your search at a statement reading a string _ending_ in `"getLoggedInUser()"` and continue searching down.**
- After a quick succession of Qt calls, the reference statement precedes `QByteArray::~QByteArray` by a few lines.
  - **Narrow your search to begin at a `call qword ptr ds:[<public: __cdecl QByteArray::~QByteArray(void)>]`.**
  - Note that x64dbg automatically populates Qt function names.
- The reference statement is immediately before some dynamic memory allocation of 0x18 bytes which precedes a null-check if-block;
  - **End your search at a `call` which closely precedes a `test rax,rax`, and**
  - **Look _immediately before_ any statement which references 0x18 as a constant.**
- Of course, the function address is being _read_, not called on, so your function address at a `lea rXX,qword ptr[XXX]` instruction.

In Studio v463, the address of `ILoginManager::loginSuccess` is `1402FD6D0`.

### Placing the call to `ILoginManager::loginSuccess`

I've chosen to place the call to `ILoginManager::loginSuccess` _at the end_ of the initialisation function `LoginManager::initialize` because:

1. it only runs once upon startup, and
2. you don't have to perform an entire function call to retrieve the `LoginManager` instance; it's stored right in `rsi`.

Be careful; space is tight.

**In 64-bit binaries**, you could follow this example, changing `1402FD6D0` to any other address you may need:

```patch
-00000001403B51FF | 48:81C4 80000000         | add rsp,80
-00000001403B5206 | 41:5F                    | pop r15
-00000001403B5208 | 41:5E                    | pop r14
-00000001403B520A | 41:5D                    | pop r13
-00000001403B520C | 41:5C                    | pop r12
-00000001403B520E | 5F                       | pop rdi
-00000001403B520F | 5E                       | pop rsi
-00000001403B5210 | 5D                       | pop rbp
-00000001403B5211 | C3                       | ret
-00000001403B5212 | CC                       | int3
-00000001403B5213 | CC                       | int3
-00000001403B5214 | CC                       | int3
-00000001403B5215 | CC                       | int3
-00000001403B5216 | CC                       | int3
-00000001403B5217 | CC                       | int3
-00000001403B5218 | CC                       | int3
-00000001403B5219 | CC                       | int3
-00000001403B521A | CC                       | int3
-00000001403B521B | CC                       | int3
-00000001403B521C | CC                       | int3
-00000001403B521D | CC                       | int3
-00000001403B521E | CC                       | int3
+00000001403B51FF | 48:89F1                  | mov rcx,rsi
+00000001403B5202 | 48:8B5424 10             | mov rdx,qword ptr ss:[rsp+10]
+00000001403B5207 | E8 C484F4FF              | call robloxstudiobeta.1402FD6D0
+00000001403B520C | 48:81C4 80000000         | add rsp,80
+00000001403B5213 | 41:5F                    | pop r15
+00000001403B5215 | 41:5E                    | pop r14
+00000001403B5217 | 41:5D                    | pop r13
+00000001403B5219 | 41:5C                    | pop r12
+00000001403B521B | 5F                       | pop rdi
+00000001403B521C | 5E                       | pop rsi
+00000001403B521D | 5D                       | pop rbp
+00000001403B521E | C3                       | ret
00000001403B521F | CC                       | int3
```
