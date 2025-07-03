

def step(images, labels, train_type, optimizer, model, loss_func, params, grade, train=False):
    if train_type == None or train_type == 'default':
        outputs = model(images)
        loss = loss_func(outputs, labels)
        if train==True:
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        all_losses = {'total_loss':loss, 'loss':loss}

    elif train_type == 'drloc':
        outputs, drloc_loss = model(images, params['m'])
        loss = loss_func(outputs, labels)
        total_loss = loss + params['lambda_'] * drloc_loss
        if train==True:
            optimizer.zero_grad()
            total_loss.backward()
            optimizer.step()

        all_losses = {'total_loss':total_loss, 'loss':loss, 'drloc_loss':drloc_loss}

    elif train_type == 'local_guidance':
        beta = params['distillation_weight']
        outputs, distillation_loss = model(images)
        reg_loss = loss_func(outputs, labels)
        total_loss = reg_loss + beta * distillation_loss
        if train==True:
            optimizer.zero_grad()
            total_loss.backward()
            optimizer.step()

        all_losses = {'total_loss':total_loss, 'loss':reg_loss, 'distillation_loss':distillation_loss}

    elif train_type == 'grade_layer':
        outputs = model(images, grade)
        loss = loss_func(outputs, labels)
        if train==True:
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        all_losses = {'total_loss':loss, 'loss':loss}

    else:
        raise ValueError(f"wrong train_type: {train_type}")

    return all_losses, outputs