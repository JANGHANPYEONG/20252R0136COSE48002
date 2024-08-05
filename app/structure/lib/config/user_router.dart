//
//
// 페이지 경로.
//
//

import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:structure/model/meat_model.dart';
import 'package:structure/model/user_model.dart';
import 'package:structure/screen/data_management/normal/edit_meat_data_screen.dart';
import 'package:structure/screen/data_management/normal/not_editable/sensory_eval_not_editable_sceen.dart';
import 'package:structure/screen/data_management/normal/not_editable/meat_image_not_editable_screen.dart';
import 'package:structure/screen/data_management/normal/not_editable/meat_info_not_editable_screen.dart';
import 'package:structure/screen/data_management/researcher/data_add_processed_meat_screen.dart';
import 'package:structure/screen/data_management/researcher/data_add_raw_meat_screen.dart';
import 'package:structure/screen/data_management/researcher/data_add_screen.dart';
import 'package:structure/screen/data_management/normal/data_management_home_screen.dart';
import 'package:structure/screen/data_management/researcher/data_management_home_tab_screen.dart';
import 'package:structure/screen/data_management/researcher/insertion_heated_sensory_screen.dart';
import 'package:structure/screen/data_management/researcher/insertion_lab_data_screen.dart';
import 'package:structure/screen/data_management/researcher/insertion_tongue_data_screen.dart';
import 'package:structure/screen/home_screen.dart';
import 'package:structure/screen/meat_registration/camera_screen.dart';
import 'package:structure/screen/meat_registration/creation_management_num_screen.dart';
import 'package:structure/screen/meat_registration/insertion_meat_info_screen.dart';
import 'package:structure/screen/meat_registration/insertion_trace_num_screen.dart';
import 'package:structure/screen/meat_registration/insertion_meat_image_screen.dart';
import 'package:structure/screen/my_page/change_password_screen.dart';
import 'package:structure/screen/my_page/delete_user_screen.dart';
import 'package:structure/screen/my_page/user_detail_screen.dart';
import 'package:structure/screen/my_page/my_page_screen.dart';
import 'package:structure/screen/sign_in/password_reset_screen.dart';
import 'package:structure/screen/sign_in/complete_reset_screen.dart';
import 'package:structure/screen/sign_up/complete_sign_up_screen.dart';
import 'package:structure/screen/meat_registration/insertion_sensory_eval_screen.dart';
import 'package:structure/screen/sign_up/insertion_user_detail_screen.dart';
import 'package:structure/screen/sign_up/insertion_user_info_screen.dart';
import 'package:structure/screen/meat_registration/meat_registration_screen.dart';
import 'package:structure/screen/sign_in/sign_in_screen.dart';
import 'package:structure/viewModel/data_management/researcher/add_processed_meat_view_model.dart';
import 'package:structure/viewModel/data_management/researcher/add_raw_meat_view_model.dart';
import 'package:structure/viewModel/data_management/researcher/data_add_home_view_model.dart';
import 'package:structure/viewModel/data_management/normal/data_management_view_model.dart';
import 'package:structure/viewModel/data_management/normal/edit_meat_data_view_model.dart';
import 'package:structure/viewModel/data_management/normal/not_editable/sensory_eval_not_editable_view_model.dart';
import 'package:structure/viewModel/data_management/normal/not_editable/insertion_meat_image_not_editable_view_model.dart';
import 'package:structure/viewModel/data_management/normal/not_editable/insertion_meat_info_not_editable_view_model.dart';
import 'package:structure/viewModel/data_management/researcher/data_management_home_tab_view_model.dart';
import 'package:structure/viewModel/data_management/researcher/insertion_heated_sensory_view_model.dart';
import 'package:structure/viewModel/data_management/researcher/insertion_lab_data_view_model.dart';
import 'package:structure/viewModel/data_management/researcher/insertion_tongue_data_view_model.dart';
import 'package:structure/viewModel/home_view_model.dart';
import 'package:structure/viewModel/meat_registration/camera_view_model.dart';
import 'package:structure/viewModel/meat_registration/creation_management_num_view_model.dart.dart';
import 'package:structure/viewModel/meat_registration/insertion_sensory_eval_view_model.dart';
import 'package:structure/viewModel/meat_registration/insertion_meat_info_view_model.dart';
import 'package:structure/viewModel/meat_registration/insertion_trace_num_view_model.dart';
import 'package:structure/viewModel/meat_registration/insertion_meat_image_view_model.dart';
import 'package:structure/viewModel/my_page/change_password_view_model.dart';
import 'package:structure/viewModel/my_page/delete_user_view_model.dart';
import 'package:structure/viewModel/my_page/user_detail_view_model.dart';
import 'package:structure/viewModel/my_page/user_info_view_model.dart';
import 'package:structure/viewModel/sign_in/password_reset_view_model.dart';
import 'package:structure/viewModel/sign_up/insertion_user_detail_view_model.dart';
import 'package:structure/viewModel/sign_up/insertion_user_info_view_model.dart';
import 'package:structure/viewModel/meat_registration/meat_registration_view_model.dart';
import 'package:structure/viewModel/sign_in/sign_in_view_model.dart';

class UserRouter {
  final MeatModel meatModel;
  final UserModel userModel;
  UserRouter({required this.meatModel, required this.userModel});

  static GoRouter getRouter(MeatModel meatModel, UserModel userModel) {
    return GoRouter(
      initialLocation: '/sign-in',
      routes: [
        // 로그인
        GoRoute(
          path: '/sign-in',
          builder: (context, state) => ChangeNotifierProvider(
            create: (context) =>
                SignInViewModel(userModel: userModel, meatModel: meatModel),
            child: const SignInScreen(),
          ),
          routes: [
            // 회원가입
            GoRoute(
              path: 'sign-up',
              builder: (context, state) => ChangeNotifierProvider(
                create: (context) => InsertionUserInfoViewModel(userModel),
                child: const InsertionUserInfoScreen(),
              ),
              routes: [
                GoRoute(
                  path: 'user-detail',
                  builder: (context, state) => ChangeNotifierProvider(
                    create: (context) =>
                        InsertionUserDetailViewModel(userModel: userModel),
                    child: const InsertionUserDetailScreen(),
                  ),
                ),
              ],
            ),
            // 비밀번호 변경
            GoRoute(
              path: 'password_reset',
              builder: (context, state) => ChangeNotifierProvider(
                create: (context) =>
                    PasswordResetViewModel(userModel: userModel),
                child: const PasswordResetScreen(),
              ),
            ),
            // 비밀번호 변경 완료
            GoRoute(
              path: 'complete_password_reset',
              builder: (context, state) => const CompleteResetScreen(),
            ),
            // 회원가입 완료
            GoRoute(
              path: 'complete-sign-up',
              builder: (context, state) => const CompleteSignUpScreen(),
            ),
          ],
        ),
        // 메인 페이지
        GoRoute(
          path: '/home',
          builder: (context, state) => ChangeNotifierProvider(
            create: (context) => HomeViewModel(userModel: userModel),
            child: const HomeScreen(),
          ),
          routes: [
            // 육류 등록 페이지
            GoRoute(
              path: 'registration',
              builder: (context, state) => ChangeNotifierProvider(
                create: (context) => MeatRegistrationViewModel(
                    meatModel: meatModel, userModel: userModel),
                child: MeatRegistrationScreen(meatModel: meatModel),
              ),
              routes: [
                // 관리번호 검색
                GoRoute(
                  path: 'trace-num',
                  builder: (context, state) => ChangeNotifierProvider(
                    create: (context) => InsertionTraceNumViewModel(meatModel),
                    child: const InsertionTraceNumScreen(),
                  ),
                  routes: [
                    // 육류 분류
                    GoRoute(
                      path: 'meat-info',
                      builder: (context, state) => ChangeNotifierProvider(
                        create: (context) =>
                            InsertionMeatInfoViewModel(meatModel),
                        child: const InsertionMeatInfoScreen(),
                      ),
                    ),
                  ],
                ),
                // 육류 이미지
                GoRoute(
                  path: 'image',
                  builder: (context, state) => ChangeNotifierProvider(
                    create: (context) =>
                        InsertionMeatImageViewModel(meatModel, userModel, true),
                    child: const InsertionMeatImageScreen(),
                  ),
                  routes: [
                    // 사진 촬영 카메라
                    GoRoute(
                      path: 'camera',
                      builder: (context, state) => ChangeNotifierProvider(
                        create: (context) => CameraViewModel(),
                        child: const CameraScreen(),
                      ),
                    ),
                  ],
                ),
                // 원육 관능평가
                GoRoute(
                  path: 'freshmeat',
                  builder: (context, state) => ChangeNotifierProvider(
                    create: (context) =>
                        InsertionSensoryEvalViewModel(meatModel, userModel),
                    child: const InsertionSensoryEvalScreen(),
                  ),
                ),
              ],
            ),
            // 육류 등록 완료 페이지
            GoRoute(
              path: 'success-registration',
              builder: (context, state) => ChangeNotifierProvider(
                create: (context) =>
                    CreationManagementNumViewModel(meatModel, userModel),
                child: const CreationManagementNumScreen(),
              ),
            ),
            // 마이 페이지
            GoRoute(
              path: 'my-page',
              builder: (context, state) => ChangeNotifierProvider(
                create: (context) => UserInfoViewModel(userModel),
                child: const MyPageScreen(),
              ),
              routes: [
                // 유저 상세 정보
                GoRoute(
                  path: 'user-detail',
                  builder: (context, state) => ChangeNotifierProvider(
                    create: (context) => UserDetailViewModel(userModel),
                    child: const UserDetailScreen(),
                  ),
                ),
                // 비밀번호 변경
                GoRoute(
                  path: 'change-pw',
                  builder: (context, state) => ChangeNotifierProvider(
                    create: (context) =>
                        ChangePasswordViewModel(userModel: userModel),
                    child: const ChangePasswordScreen(),
                  ),
                ),
                // 회원 탈퇴
                GoRoute(
                  path: 'delete-user',
                  builder: (context, state) => ChangeNotifierProvider(
                    create: (context) =>
                        DeleteUserViewModel(userModel: userModel),
                    child: const DeleteUserScreen(),
                  ),
                )
              ],
            ),
            // 데이터 관리 페이지 - Normal User
            GoRoute(
              path: 'data-manage-normal',
              builder: (context, state) => ChangeNotifierProvider(
                create: (context) => DataManagementHomeViewModel(userModel),
                child: const DataManagementHomeScreen(),
              ),
              routes: [
                // 데이터 수정
                GoRoute(
                  path: 'edit',
                  builder: (context, state) => ChangeNotifierProvider(
                    create: (context) =>
                        EditMeatDataViewModel(meatModel, userModel),
                    child: const EditMeatDataScreen(),
                  ),
                  routes: [
                    // 수정불가
                    GoRoute(
                      path: 'info',
                      builder: (context, state) => ChangeNotifierProvider(
                        create: (context) =>
                            InsertionMeatInfoNotEditableViewModel(meatModel),
                        child: const MeatInfoNotEditableScreen(),
                      ),
                    ),
                    GoRoute(
                      path: 'image',
                      builder: (context, state) => ChangeNotifierProvider(
                        create: (context) =>
                            InsertionMeatImageNotEditableViewModel(meatModel),
                        child: const MeatImageNotEditableScreen(),
                      ),
                    ),
                    GoRoute(
                      path: 'freshmeat',
                      builder: (context, state) => ChangeNotifierProvider(
                        create: (context) =>
                            SensoryEvalNotEditableViewModel(meatModel, false),
                        child: const SensoryEvalNotEditableScreen(),
                      ),
                    ),
                    // 수정 가능
                    GoRoute(
                      path: 'info-editable',
                      builder: (context, state) => ChangeNotifierProvider(
                        create: (context) =>
                            InsertionMeatInfoViewModel(meatModel),
                        child: const InsertionMeatInfoScreen(),
                      ),
                    ),
                    GoRoute(
                      path: 'image-editable',
                      builder: (context, state) => ChangeNotifierProvider(
                        create: (context) => InsertionMeatImageViewModel(
                            meatModel, userModel, true),
                        child: const InsertionMeatImageScreen(),
                      ),
                    ),
                    GoRoute(
                      path: 'freshmeat-editable',
                      builder: (context, state) => ChangeNotifierProvider(
                        create: (context) =>
                            InsertionSensoryEvalViewModel(meatModel, userModel),
                        child: const InsertionSensoryEvalScreen(),
                      ),
                    ),
                  ],
                ),
              ],
            ),
            // 데이터 관리 페이지 - Researcher User
            GoRoute(
              path: 'data-manage-researcher',
              builder: (context, state) => ChangeNotifierProvider(
                create: (context) =>
                    DataManagementHomeTabViewModel(meatModel, userModel),
                child: const DataManagementHomeTabScreen(),
              ),
              routes: [
                GoRoute(
                  path: 'add',
                  builder: (context, state) => ChangeNotifierProvider(
                    create: (context) => DataAddHomeViewModel(meatModel),
                    child: const DataAddScreen(),
                  ),
                  routes: [
                    GoRoute(
                      path: 'raw-meat',
                      builder: (context, state) => ChangeNotifierProvider(
                        create: (context) => AddRawMeatViewModel(),
                        child: DataAddRawMeatScreen(meatModel: meatModel),
                      ),
                      routes: [
                        // 수정 불가 원육 기본정보
                        GoRoute(
                          path: 'info',
                          builder: (context, state) => ChangeNotifierProvider(
                            create: (context) =>
                                InsertionMeatInfoNotEditableViewModel(
                                    meatModel),
                            child: const MeatInfoNotEditableScreen(),
                          ),
                        ),
                        // 수정 불가 원육 단면 촬영
                        GoRoute(
                          path: 'image-noteditable',
                          builder: (context, state) => ChangeNotifierProvider(
                            create: (context) =>
                                InsertionMeatImageNotEditableViewModel(
                                    meatModel),
                            child: const MeatImageNotEditableScreen(),
                          ),
                        ),
                        // 수정 불가 원육 관능평가
                        GoRoute(
                          path: 'sensory',
                          builder: (context, state) => ChangeNotifierProvider(
                            create: (context) =>
                                SensoryEvalNotEditableViewModel(
                                    meatModel, false),
                            child: const SensoryEvalNotEditableScreen(),
                          ),
                        ),
                        // 원육 전자혀 데이터
                        GoRoute(
                          path: 'tongue',
                          builder: (context, state) => ChangeNotifierProvider(
                            create: (context) => InsertionTongueDataViewModel(
                                meatModel, userModel, true),
                            child: const InsertionTongueDataScreen(),
                          ),
                        ),
                        // 원육 실험 데이터
                        GoRoute(
                          path: 'lab',
                          builder: (context, state) => ChangeNotifierProvider(
                            create: (context) => InsertionLabDataViewModel(
                                meatModel, userModel, true),
                            child: const InsertionLabDataScreen(),
                          ),
                        ),
                        // 가열육 단면 촬영
                        GoRoute(
                          path: 'heated-image',
                          builder: (context, state) => ChangeNotifierProvider(
                            create: (context) => InsertionMeatImageViewModel(
                                meatModel, userModel, false),
                            child: const InsertionMeatImageScreen(),
                          ),
                        ),
                        // 가열육 관능평가 데이터
                        GoRoute(
                          path: 'heated-sensory',
                          builder: (context, state) => ChangeNotifierProvider(
                            create: (context) =>
                                InsertionHeatedSensoryViewModel(
                                    meatModel, userModel),
                            child: const InsertionHeatedSensoryScreen(),
                          ),
                        ),
                        GoRoute(
                          path: 'heated-tongue',
                          builder: (context, state) => ChangeNotifierProvider(
                            create: (context) => InsertionTongueDataViewModel(
                                meatModel, userModel, false),
                            child: const InsertionTongueDataScreen(),
                          ),
                        ),
                        // 원육 실험 데이터
                        GoRoute(
                          path: 'heated-lab',
                          builder: (context, state) => ChangeNotifierProvider(
                            create: (context) => InsertionLabDataViewModel(
                                meatModel, userModel, false),
                            child: const InsertionLabDataScreen(),
                          ),
                        ),
                      ],
                    ),
                    GoRoute(
                      path: 'processed-meat',
                      builder: (context, state) => ChangeNotifierProvider(
                        create: (context) => AddProcessedMeatViewModel(),
                        child: DataAddProcessedMeatScreen(meatModel: meatModel),
                      ),
                      routes: [
                        GoRoute(
                          path: 'image',
                          builder: (context, state) => ChangeNotifierProvider(
                            create: (context) => InsertionMeatImageViewModel(
                                meatModel, userModel, true),
                            child: const InsertionMeatImageScreen(),
                          ),
                        ),
                        GoRoute(
                          path: 'sensory',
                          builder: (context, state) => ChangeNotifierProvider(
                            create: (context) => InsertionSensoryEvalViewModel(
                                meatModel, userModel),
                            child: const InsertionSensoryEvalScreen(),
                          ),
                        ),
                        GoRoute(
                          path: 'tongue',
                          builder: (context, state) => ChangeNotifierProvider(
                            create: (context) => InsertionTongueDataViewModel(
                                meatModel, userModel, true),
                            child: const InsertionTongueDataScreen(),
                          ),
                        ),
                        GoRoute(
                          path: 'lab',
                          builder: (context, state) => ChangeNotifierProvider(
                            create: (context) => InsertionLabDataViewModel(
                                meatModel, userModel, true),
                            child: const InsertionLabDataScreen(),
                          ),
                        ),
                        GoRoute(
                          path: 'heated-image',
                          builder: (context, state) => ChangeNotifierProvider(
                            create: (context) => InsertionMeatImageViewModel(
                                meatModel, userModel, false),
                            child: const InsertionMeatImageScreen(),
                          ),
                        ),
                        GoRoute(
                          path: 'heated-sensory',
                          builder: (context, state) => ChangeNotifierProvider(
                            create: (context) =>
                                InsertionHeatedSensoryViewModel(
                                    meatModel, userModel),
                            child: const InsertionHeatedSensoryScreen(),
                          ),
                        ),
                        GoRoute(
                          path: 'heated-tongue',
                          builder: (context, state) => ChangeNotifierProvider(
                            create: (context) => InsertionTongueDataViewModel(
                                meatModel, userModel, false),
                            child: const InsertionTongueDataScreen(),
                          ),
                        ),
                        GoRoute(
                          path: 'heated-lab',
                          builder: (context, state) => ChangeNotifierProvider(
                            create: (context) => InsertionLabDataViewModel(
                                meatModel, userModel, false),
                            child: const InsertionLabDataScreen(),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                GoRoute(
                  path: 'approve',
                  builder: (context, state) => ChangeNotifierProvider(
                    create: (context) =>
                        EditMeatDataViewModel(meatModel, userModel),
                    child: const EditMeatDataScreen(),
                  ),
                  routes: [
                    // 수정불가
                    GoRoute(
                      path: 'info',
                      builder: (context, state) => ChangeNotifierProvider(
                        create: (context) =>
                            InsertionMeatInfoNotEditableViewModel(meatModel),
                        child: const MeatInfoNotEditableScreen(),
                      ),
                    ),
                    GoRoute(
                      path: 'image',
                      builder: (context, state) => ChangeNotifierProvider(
                        create: (context) =>
                            InsertionMeatImageNotEditableViewModel(meatModel),
                        child: const MeatImageNotEditableScreen(),
                      ),
                    ),
                    GoRoute(
                      path: 'freshmeat',
                      builder: (context, state) => ChangeNotifierProvider(
                        create: (context) =>
                            SensoryEvalNotEditableViewModel(meatModel, false),
                        child: const SensoryEvalNotEditableScreen(),
                      ),
                    ),
                  ],
                )
              ],
            ),
          ],
        ),
      ],
    );
  }
}
