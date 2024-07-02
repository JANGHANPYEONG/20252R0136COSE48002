import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/main_input_field.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/sign_up/insertion_user_info_view_model.dart';
import 'package:structure/components/loading_screen.dart';

class InsertionUserInfoScreen extends StatefulWidget {
  const InsertionUserInfoScreen({super.key});

  @override
  State<InsertionUserInfoScreen> createState() =>
      _InsertionUserInfoScreenState();
}

class _InsertionUserInfoScreenState extends State<InsertionUserInfoScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: const CustomAppBar(
        backButton: true,
        closeButton: false,
        title: '회원가입',
      ),
      body: GestureDetector(
        onTap: () => FocusScope.of(context).unfocus(),
        child: Stack(
          children: [
            SingleChildScrollView(
              child: Form(
                key: context.read<InsertionUserInfoViewModel>().formKey,
                child: Column(
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        SizedBox(
                          height: 30.h,
                        ),
                        Container(
                          margin: EdgeInsets.only(left: 40.w),
                          alignment: Alignment.centerLeft,
                          child: Text(
                            '이름',
                            style: Palette.fieldTitle,
                          ),
                        ),
                        SizedBox(
                          height: 8.h,
                        ),
                        MainInputField(
                          mode: 1,
                          width: 640.w,
                          controller:
                              context.read<InsertionUserInfoViewModel>().name,
                        ),
                        SizedBox(
                          height: 30.h,
                        ),
                        Container(
                          margin: EdgeInsets.only(left: 40.w),
                          alignment: Alignment.centerLeft,
                          child: Text(
                            '이메일',
                            style: Palette.fieldTitle,
                          ),
                        ),
                        SizedBox(
                          height: 8.h,
                        ),
                        Stack(
                          children: [
                            // 이메일 입력 필드
                            MainInputField(
                              formKey: context
                                  .read<InsertionUserInfoViewModel>()
                                  .formKey,
                              mode: 1,
                              width: 640.w,
                              controller: context
                                  .read<InsertionUserInfoViewModel>()
                                  .email,
                              validateFunc: (value) => context
                                  .read<InsertionUserInfoViewModel>()
                                  .idValidate(value),
                              onChangeFunc: (value) => context
                                  .read<InsertionUserInfoViewModel>()
                                  .onChangeEmail(value),
                              contentPadding:
                                  EdgeInsets.only(left: 30.w, right: 200.w),
                            ),
                            // 중복확인 버튼
                            Positioned(
                              right: 30.w,
                              child: TextButton(
                                onPressed: context
                                        .watch<InsertionUserInfoViewModel>()
                                        .isUnique
                                    ? null
                                    : () => context
                                            .read<InsertionUserInfoViewModel>()
                                            .isValidId
                                        ? context
                                            .read<InsertionUserInfoViewModel>()
                                            .dupliCheck(context)
                                        : null,
                                child: context
                                        .read<InsertionUserInfoViewModel>()
                                        .isUnique
                                    ? const Icon(
                                        Icons.check,
                                        color: Palette.mainBtnAtvBg,
                                      )
                                    : Text(
                                        '중복확인',
                                        style: Palette.fieldContent
                                            .copyWith(color: Colors.black),
                                      ),
                              ),
                            ),
                          ],
                        ),
                        SizedBox(
                          height: 30.h,
                        ),
                        Container(
                          margin: EdgeInsets.only(left: 40.w),
                          alignment: Alignment.centerLeft,
                          child: Text(
                            '비밀번호',
                            style: Palette.fieldTitle,
                          ),
                        ),
                        SizedBox(
                          height: 8.h,
                        ),
                        // 비밀번호 입력 필드
                        MainInputField(
                          formKey: context
                              .read<InsertionUserInfoViewModel>()
                              .formKey,
                          mode: 1,
                          obscureText: true,
                          width: 640.w,
                          controller: context
                              .read<InsertionUserInfoViewModel>()
                              .password,
                          validateFunc: (value) => context
                              .read<InsertionUserInfoViewModel>()
                              .pwValidate(value),
                          hintText: '영문 대/소문자+숫자+특수문자',
                        ),
                        SizedBox(
                          height: 16.h,
                        ),
                        MainInputField(
                          formKey: context
                              .read<InsertionUserInfoViewModel>()
                              .formKey,
                          mode: 1,
                          obscureText: true,
                          width: 640.w,
                          controller: context
                              .read<InsertionUserInfoViewModel>()
                              .cPassword,
                          validateFunc: (value) => context
                              .read<InsertionUserInfoViewModel>()
                              .cPwValidate(value),
                          hintText: '비밀번호 확인',
                        ),
                      ],
                    ),
                    SizedBox(
                      height: 32.h,
                    ),
                    Container(
                      decoration: BoxDecoration(
                          border: Border.all(
                            color: Palette.fieldBorder,
                          ),
                          borderRadius: BorderRadius.circular(15.sp)),
                      width: 640.h,
                      child: Column(children: [
                        Row(
                          children: [
                            Checkbox(
                              value: context
                                  .watch<InsertionUserInfoViewModel>()
                                  .isChecked1,
                              onChanged: (value) => context
                                  .read<InsertionUserInfoViewModel>()
                                  .clicked1stCheckBox(value),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(10),
                              ),
                              activeColor: Palette.mainBtnAtvBg,
                              checkColor: Colors.white,
                            ),
                            Text(
                              '약관 전체 동의',
                              style: Palette.h5,
                            ),
                          ],
                        ),
                        SizedBox(
                          width: 640.w,
                          child: const Divider(
                            height: 0,
                          ),
                        ),
                        Row(
                          children: [
                            Checkbox(
                              value: context
                                  .watch<InsertionUserInfoViewModel>()
                                  .isChecked2,
                              onChanged: (value) => context
                                  .read<InsertionUserInfoViewModel>()
                                  .clicked2ndCheckBox(value),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(10),
                              ),
                              activeColor: Palette.mainBtnAtvBg,
                              checkColor: Colors.white,
                            ),
                            Text(
                              '(필수) 개인정보 수집/제공 동의',
                              style: Palette.h5,
                            ),
                            const Spacer(),
                            InkWell(
                              onTap: () => showTermsPopup(context),
                              child: Container(
                                margin: EdgeInsets.only(right: 24.w),
                                child: Icon(
                                  Icons.arrow_forward_ios,
                                  size: 20.sp,
                                ),
                              ),
                            )
                          ],
                        ),
                        Row(
                          children: [
                            Checkbox(
                              value: context
                                  .watch<InsertionUserInfoViewModel>()
                                  .isChecked3,
                              onChanged: (value) => context
                                  .read<InsertionUserInfoViewModel>()
                                  .clicked3rdCheckBox(value),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(10),
                              ),
                              activeColor: Palette.mainBtnAtvBg,
                              checkColor: Colors.white,
                            ),
                            Text(
                              '(필수) 제 3자 정보 제공 동의',
                              style: Palette.h5,
                            ),
                            const Spacer(),
                            InkWell(
                              onTap: () => showTermsPopup(context),
                              child: Container(
                                margin: EdgeInsets.only(right: 24.w),
                                child: Icon(
                                  Icons.arrow_forward_ios,
                                  size: 20.sp,
                                ),
                              ),
                            )
                          ],
                        ),
                        Row(
                          children: [
                            Checkbox(
                              value: context
                                  .watch<InsertionUserInfoViewModel>()
                                  .isChecked4,
                              onChanged: (value) => context
                                  .read<InsertionUserInfoViewModel>()
                                  .clicked4thCheckBox(value),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(10),
                              ),
                              activeColor: Palette.mainBtnAtvBg,
                              checkColor: Colors.white,
                            ),
                            Text(
                              '(선택) 알림받기',
                              style: Palette.h5,
                            ),
                          ],
                        ),
                      ]),
                    ),
                    Container(
                      margin: EdgeInsets.symmetric(vertical: 40.h),
                      child: MainButton(
                        mode: 1,
                        onPressed: context
                                .read<InsertionUserInfoViewModel>()
                                .isAllChecked()
                            ? () => context
                                .read<InsertionUserInfoViewModel>()
                                .clickedNextButton(context)
                            : null,
                        text: '다음',
                        width: 640.w,
                        height: 96.h,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            Center(
              child: // 데이터를 처리하는 동안 로딩 위젯 보여주기
                  context.watch<InsertionUserInfoViewModel>().emailCheckLoading
                      ? const LoadingScreen()
                      : Container(),
            ),
          ],
        ),
      ),
    );
  }
}
