![](image.png)

In Studio v463, I've had problems getting the _Insert Objects_ window to show anything more than a curation of seven items in the _Frequently Used_ section. The variety of items changes per the ClassName of any object(s) you have selected.

To work around this problem, you can run the following in the command bar:

```lua
Instance.new('{OBJECT_TYPE}', game.Selection:Get()[1])
```

### `InsertObjectWidget::populateList` Testing

One might think that patching `InsertObjectWidget::populateList` could fix it.

However, **that is an incorrect approach**.

According to the v548 PDB symbols, the same method is externally called _once_. The caller in question is `RBX::InsertObjectUtils::createWidgets`, which contains the following strings in v548:

1. `"DataStoreService"`
2. `"Studio"`
3. `"AnalyticsService"`

The precise location of `populateList` comes immediately before an if-statement, followed later by a call to `QListData::begin`:

```cpp
v40._Ptr = pDataModel->_Ptr;
v40._Rep = v27;
anonymous_namespace_::populateList(services, v26, v5, &v40, &ignoreList);
if ( v26->p.d->ref.atomic._q_value._Storage._Value > 1u )
	QList<QListWidgetItem *>::detach_helper((QList<QCheckBox *> *)v26, v26->p.d->alloc);
for ( i = QListData::begin(&v26->p); ; ++i ) ...
```

The `call` instruction is located at `00000001405148B8` in v463 Studio.

However, upon skipping the call completely, **there is no visible improvement**. Only the _Frequently Used_ items show up.

```patch
 00000001405148AE | 4C:8BC3                  | mov r8,rbx
 00000001405148B1 | 48:8BD6                  | mov rdx,rsi
 00000001405148B4 | 41:0FB6CD                | movzx ecx,r13b
 00000001405148B8 | E8 A3110000              | call robloxstudiobeta.140515A60
 00000001405148BD | 48:8B06                  | mov rax,qword ptr ds:[rsi]
 00000001405148C0 | 8338 01                  | cmp dword ptr ds:[rax],1
 00000001405148C3 | 76 0B                    | jbe robloxstudiobeta.1405148D0
 00000001405148C5 | 8B50 04                  | mov edx,dword ptr ds:[rax+4]
 00000001405148C8 | 48:8BCE                  | mov rcx,rsi
-00000001405148CB | E8 E060D5FF              | call robloxstudiobeta.14026A9B0
+00000001405148B8 | 90                       | nop
+00000001405148B9 | 90                       | nop
+00000001405148BA | 90                       | nop
+00000001405148BB | 90                       | nop
+00000001405148BC | 90                       | nop
 00000001405148D0 | 48:8BCE                  | mov rcx,rsi
 00000001405148D3 | FF15 3F43BB01            | call qword ptr ds:[<public: void ** __cdecl QListData::begin(void) const>]
```

| Before         | After          |
| -------------- | -------------- |
| ![](image.png) | ![](image.png) |
