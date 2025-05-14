
class BaseChatOpenAI(BaseChatModel):
    client: Any = Field(default=None, exclude=True)  #: :meta private:
    async_client: Any = Field(default=None, exclude=True)  #: :meta private:
    root_client: Any = Field(default=None, exclude=True)  #: :meta private:
    root_async_client: Any = Field(default=None, exclude=True)  #: :meta private:
    model_name: str = Field(default="gpt-3.5-turbo", alias="model")
    """Model name to use."""
    temperature: Optional[float] = None
    """What sampling temperature to use."""
    model_kwargs: dict[str, Any] = Field(default_factory=dict)
    """Holds any model parameters valid for `create` call not explicitly specified."""
    
    def _generate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        if self.streaming:
            stream_iter = self._stream(
                messages, stop=stop, run_manager=run_manager, **kwargs
            )
            return generate_from_stream(stream_iter)
        payload = self._get_request_payload(messages, stop=stop, **kwargs)
        generation_info = None
        if "response_format" in payload:
            if self.include_response_headers:
                warnings.warn(
                    "Cannot currently include response headers when response_format is "
                    "specified."
                )
            payload.pop("stream")
            try:
                response = self.root_client.beta.chat.completions.parse(**payload)
            except openai.BadRequestError as e:
                _handle_openai_bad_request(e)
        elif self._use_responses_api(payload):
            original_schema_obj = kwargs.get("response_format")
            if original_schema_obj and _is_pydantic_class(original_schema_obj):
                response = self.root_client.responses.parse(**payload)
            else:
                if self.include_response_headers:
                    raw_response = self.root_client.with_raw_response.responses.create(
                        **payload
                    )
                    response = raw_response.parse()
                    generation_info = {"headers": dict(raw_response.headers)}
                else:
                    response = self.root_client.responses.create(**payload)
            return _construct_lc_result_from_responses_api(
                response, schema=original_schema_obj, metadata=generation_info
            )
        elif self.include_response_headers:
            raw_response = self.client.with_raw_response.create(**payload)
            response = raw_response.parse()
            generation_info = {"headers": dict(raw_response.headers)}
        else:
            response = self.client.create(**payload)
        return self._create_chat_result(response, generation_info)

    def _get_request_payload(
        self,
        input_: LanguageModelInput,
        *,
        stop: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> dict:
        messages = self._convert_input(input_).to_messages()
        if stop is not None:
            kwargs["stop"] = stop

        payload = {**self._default_params, **kwargs}
        if self._use_responses_api(payload):
            payload = _construct_responses_api_payload(messages, payload)
        else:
            payload["messages"] = [_convert_message_to_dict(m) for m in messages]
        return payload
