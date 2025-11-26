@extends('admin::layout')

@component('admin::components.page.header')
    @slot('title', trans('comment::comment.create_comment'))

    <li><a href="{{ route('admin.comments.index') }}">{{ trans('comment::comment.comments') }}</a></li>
    <li class="active">{{ trans('comment::comment.create_comment') }}</li>
@endcomponent

@section('content')
    <div class="row">
        <div class="col-md-12">
            <form method="POST" action="{{ route('admin.comments.store') }}" id="comment-create-form" class="form-horizontal">
                {{ csrf_field() }}

                <div class="box box-primary">
                    <div class="box-body">
                        <div class="form-group {{ $errors->has('content') ? 'has-error' : '' }}">
                            <label for="content" class="col-md-3 control-label">
                                {{ trans('comment::comment.content') }} <span class="text-red">*</span>
                            </label>
                            <div class="col-md-9">
                                <textarea name="content" class="form-control" id="content" rows="5" placeholder="{{ trans('comment::comment.content_placeholder') }}">{{ old('content') }}</textarea>
                                @if ($errors->has('content'))
                                    <span class="help-block">{{ $errors->first('content') }}</span>
                                @endif
                            </div>
                        </div>

                        <div class="form-group {{ $errors->has('platform') ? 'has-error' : '' }}">
                            <label for="platform" class="col-md-3 control-label">
                                {{ trans('comment::comment.platform') }} <span class="text-red">*</span>
                            </label>
                            <div class="col-md-9">
                                <select name="platform" class="form-control" id="platform">
                                    <option value="">{{ trans('comment::comment.select_platform') }}</option>
                                    <option value="facebook" {{ old('platform') === 'facebook' ? 'selected' : '' }}>Facebook</option>
                                    <option value="youtube" {{ old('platform') === 'youtube' ? 'selected' : '' }}>YouTube</option>
                                    <option value="twitter" {{ old('platform') === 'twitter' ? 'selected' : '' }}>Twitter</option>
                                    <option value="tiktok" {{ old('platform') === 'tiktok' ? 'selected' : '' }}>TikTok</option>
                                    <option value="instagram" {{ old('platform') === 'instagram' ? 'selected' : '' }}>Instagram</option>
                                    <option value="other" {{ old('platform') === 'other' ? 'selected' : '' }}>{{ trans('comment::comment.other_platform') }}</option>
                                </select>
                                @if ($errors->has('platform'))
                                    <span class="help-block">{{ $errors->first('platform') }}</span>
                                @endif
                            </div>
                        </div>

                        <div class="form-group {{ $errors->has('source_user_name') ? 'has-error' : '' }}">
                            <label for="source_user_name" class="col-md-3 control-label">
                                {{ trans('comment::comment.source_user_name') }}
                            </label>
                            <div class="col-md-9">
                                <input type="text" name="source_user_name" class="form-control" id="source_user_name" value="{{ old('source_user_name') }}" placeholder="{{ trans('comment::comment.source_user_name_placeholder') }}">
                                @if ($errors->has('source_user_name'))
                                    <span class="help-block">{{ $errors->first('source_user_name') }}</span>
                                @endif
                            </div>
                        </div>

                        <div class="form-group {{ $errors->has('source_url') ? 'has-error' : '' }}">
                            <label for="source_url" class="col-md-3 control-label">
                                {{ trans('comment::comment.source_url') }}
                            </label>
                            <div class="col-md-9">
                                <input type="url" name="source_url" class="form-control" id="source_url" value="{{ old('source_url') }}" placeholder="{{ trans('comment::comment.source_url_placeholder') }}">
                                @if ($errors->has('source_url'))
                                    <span class="help-block">{{ $errors->first('source_url') }}</span>
                                @endif
                            </div>
                        </div>

                        @if ($errors->has('api_error'))
                            <div class="form-group has-error">
                                <div class="col-md-offset-3 col-md-9">
                                    <span class="help-block">
                                        <strong>{{ $errors->first('api_error') }}</strong>
                                    </span>
                                </div>
                            </div>
                        @endif

                        <div class="form-group">
                            <div class="col-md-offset-3 col-md-9">
                                <button type="submit" class="btn btn-primary" data-loading>{{ trans('admin::admin.buttons.save') }}</button>
                                <a href="{{ route('admin.comments.index') }}" class="btn btn-default">
                                    {{ trans('admin::admin.buttons.back') }}
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </form>
        </div>
    </div>
@endsection
