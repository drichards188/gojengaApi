# handle ingress for AUTH service
def lambda_handler(event, context):
    # handle branch
    if event['resource'] == '/login':
        if event['method'] == 'POST':
            return {'resource': 'login POST'}
    elif event['resource'] == '/refresh':
        if event['method'] == 'POST':
            return {'resource': 'refresh POST'}


async def login_for_access_token(request: Request, is_test: Optional[bool] | None = Header(default=False),
                                 form_data: OAuth2PasswordRequestForm = Depends()):
        try:
            table_name: str = 'users'
            if is_test:
                table_name = 'usersTest'
            user = authenticate_user(table_name, form_data.username.lower(), form_data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user["name"]}, expires_delta=access_token_expires
            )
            refresh_token_expires = timedelta(days=REFRESH_ACCESS_TOKEN_EXPIRE_DAYS)
            refresh_token = create_access_token(data={"sub": user["name"]}, expires_delta=refresh_token_expires)
            return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def renew_jwt(request: Request, jwt_token: JWT):
    with tracer.start_as_current_span(
            "refreshToken",
            context=extract(request.headers),
            kind=trace.SpanKind.SERVER
    ):
        try:
            token_data = Auth.get_token_payload(jwt_token.token)
            renewed_token = Auth.renew_access_token({"sub": token_data.get("sub")}, ACCESS_TOKEN_EXPIRE_MINUTES)
            return {"token": renewed_token}
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
