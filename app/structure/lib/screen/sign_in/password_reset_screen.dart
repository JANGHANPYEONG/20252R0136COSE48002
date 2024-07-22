import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/main_input_field.dart';
import 'package:structure/viewModel/sign_in/password_reset_view_model.dart';

class PasswordResetScreen extends StatefulWidget {
  const PasswordResetScreen({super.key});

  @override
  State<PasswordResetScreen> createState() => _PasswordResetScreenState();
}

class _PasswordResetScreenState extends State<PasswordResetScreen> {
  @override
  Widget build(BuildContext context) {
    PasswordResetViewModel passwordResetViewModel =
        context.watch<PasswordResetViewModel>();

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: const CustomAppBar(
          title: '비밀번호 재설정', backButton: true, closeButton: false),
      body: Stack(
        children: [
          GestureDetector(
            onTap: () => FocusScope.of(context).unfocus(),
            child: SingleChildScrollView(
              child: Form(
                key: passwordResetViewModel.formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    SizedBox(height: 72.h),

                    // 이메일
                    Container(
                        margin: EdgeInsets.only(left: 40.w),
                        alignment: Alignment.centerLeft,
                        child: Text('이메일', style: Palette.fieldTitle)),
                    SizedBox(height: 8.h),

                    // 이메일 입력 input field
                    MainInputField(
                      mode: 1,
                      width: 640.w,
                      formKey: passwordResetViewModel.formKey,
                      controller: passwordResetViewModel.email,
                      validateFunc: (value) =>
                          passwordResetViewModel.emailValidate(value),
                    ),
                    SizedBox(height: 820.h),

                    // 재설정 버튼
                    MainButton(
                      onPressed: passwordResetViewModel.isValid()
                          ? () async =>
                              passwordResetViewModel.sendResetPassword(context)
                          : null,
                      text: '비밀번호 재설정',
                      width: 658.w,
                      height: 96.h,
                      mode: 1,
                    ),
                  ],
                ),
              ),
            ),
          ),
          passwordResetViewModel.isLoading
              ? const Center(child: LoadingScreen())
              : Container(),
        ],
      ),
    );
  }
}
