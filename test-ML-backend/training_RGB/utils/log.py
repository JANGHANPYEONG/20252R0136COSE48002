import numpy as np
import mlflow

def log(all_fold_results, cross_validation, label_names):
    num_folds = len(all_fold_results)
    num_epochs = len(all_fold_results[0][0])
    num_labels = len(label_names)

    train_losses = np.array([fold_result[0] for fold_result in all_fold_results])          # (num_folds, num_epochs)
    train_r2 = np.array([fold_result[1] for fold_result in all_fold_results])              # (num_folds, num_epochs)
    val_losses = np.array([fold_result[2] for fold_result in all_fold_results])            # (num_folds, num_epochs)
    val_r2 = np.array([fold_result[3] for fold_result in all_fold_results])                # (num_folds, num_epochs)
    val_acc_05 = np.array([[epoch_data[0] for epoch_data in fold_result[4]] for fold_result in all_fold_results])
    val_acc_10 = np.array([[epoch_data[1] for epoch_data in fold_result[4]] for fold_result in all_fold_results])
    val_acc_20 = np.array([[epoch_data[2] for epoch_data in fold_result[4]] for fold_result in all_fold_results])
    average_val_acc_05 = np.array([[epoch_data[0] for epoch_data in fold_result[5]] for fold_result in all_fold_results])
    average_val_acc_10 = np.array([[epoch_data[1] for epoch_data in fold_result[5]] for fold_result in all_fold_results])
    average_val_acc_20 = np.array([[epoch_data[2] for epoch_data in fold_result[5]] for fold_result in all_fold_results])

    # epoch별로 폴드들의 평균 값 계산
    average_train_losses = train_losses.mean(axis=0)           # (num_epochs,)
    average_train_r2 = train_r2.mean(axis=0)                   # (num_epochs,)
    average_val_losses = val_losses.mean(axis=0)               # (num_epochs,)
    average_val_r2 = val_r2.mean(axis=0)                       # (num_epochs,)
    average_val_acc_per_label_05 = val_acc_05.mean(axis=0)  # (num_epochs, num_labels)
    average_val_acc_per_label_10 = val_acc_10.mean(axis=0)  # (num_epochs, num_labels)
    average_val_acc_per_label_20 = val_acc_20.mean(axis=0)  # (num_epochs, num_labels)           # (num_epochs, num_labels)
    average_average_val_acc_05 = average_val_acc_05.mean(axis=0) # (num_epochs,)
    average_average_val_acc_10 = average_val_acc_10.mean(axis=0) # (num_epochs,)
    average_average_val_acc_20 = average_val_acc_20.mean(axis=0) # (num_epochs,)

    if cross_validation:
        for epoch in range(num_epochs):
            mlflow.log_metric('average_train_loss', average_train_losses[epoch], step=epoch + 1)
            mlflow.log_metric('average_train_r2', average_train_r2[epoch], step=epoch + 1)
            mlflow.log_metric('average_val_loss', average_val_losses[epoch], step=epoch + 1)
            mlflow.log_metric('average_val_r2', average_val_r2[epoch], step=epoch + 1)
            mlflow.log_metric('average_average_val_acc_05', average_average_val_acc_05[epoch], step=epoch + 1)
            mlflow.log_metric('average_average_val_acc_10', average_average_val_acc_10[epoch], step=epoch + 1)
            mlflow.log_metric('average_average_val_acc_20', average_average_val_acc_20[epoch], step=epoch + 1)

            for i in range(num_labels):
                label_name = label_names[i]
                mlflow.log_metric(f'average_val_acc_05_{label_name}', average_val_acc_per_label_05[epoch, i], step=epoch + 1)
                mlflow.log_metric(f'average_val_acc_10_{label_name}', average_val_acc_per_label_10[epoch, i], step=epoch + 1)
                mlflow.log_metric(f'average_val_acc_20_{label_name}', average_val_acc_per_label_20[epoch, i], step=epoch + 1)

    min_val_loss_idx = np.argmin(val_losses)
    best_fold_idx, best_epoch_idx = np.unravel_index(min_val_loss_idx, val_losses.shape)

    best_val_loss = val_losses[best_fold_idx, best_epoch_idx]
    best_val_r2 = val_r2[best_fold_idx, best_epoch_idx]
    best_val_acc_per_label_05 = val_acc_05[best_fold_idx, best_epoch_idx]
    best_val_acc_per_label_10 = val_acc_10[best_fold_idx, best_epoch_idx]
    best_val_acc_per_label_20 = val_acc_20[best_fold_idx, best_epoch_idx]
    best_average_val_acc_05 = average_val_acc_05[best_fold_idx, best_epoch_idx]
    best_average_val_acc_10 = average_val_acc_10[best_fold_idx, best_epoch_idx]
    best_average_val_acc_20 = average_val_acc_20[best_fold_idx, best_epoch_idx]

    mlflow.log_metric('best_val_loss', best_val_loss)
    mlflow.log_metric('best_val_r2', best_val_r2)
    mlflow.log_metric('best_average_val_acc_05', best_average_val_acc_05)
    mlflow.log_metric('best_average_val_acc_10', best_average_val_acc_10)
    mlflow.log_metric('best_average_val_acc_20', best_average_val_acc_20)

    for i in range(num_labels):
        label_name = label_names[i]
        mlflow.log_metric(f'best_val_acc_05_{label_name}', best_val_acc_per_label_05[i])
        mlflow.log_metric(f'best_val_acc_10_{label_name}', best_val_acc_per_label_10[i])
        mlflow.log_metric(f'best_val_acc_20_{label_name}', best_val_acc_per_label_20[i])

    # 결과 출력
    print(f"\nBest Validation Results:")
    print(f"Fold: {best_fold_idx + 1}/{num_folds}")
    print(f"Epoch: {best_epoch_idx + 1}/{num_epochs}")
    print(f"Validation Loss: {best_val_loss:.3f}")
    print(f"Validation R2: {best_val_r2:.3f}")
    print(f"Validation Accuracies (0.5): {best_val_acc_per_label_05}")
    print(f"Validation Accuracies (1.0): {best_val_acc_per_label_10}")
    print(f"Validation Accuracies (2.0): {best_val_acc_per_label_20}")
    print(f"Average Validation Accuracy (0.5): {best_average_val_acc_05:.3f}")
    print(f"Average Validation Accuracy (1.0): {best_average_val_acc_10:.3f}")
    print(f"Average Validation Accuracy (2.0): {best_average_val_acc_20:.3f}")
