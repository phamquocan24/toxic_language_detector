@component('mail::message')
# Invitation to Join Our System

You have been invited to join our system as an {{ $invitation->role == 1 ? 'Administrator' : 'Member' }}.

@component('mail::button', ['url' => route('invitation.accept', $invitation->token)])
Accept Invitation
@endcomponent

This invitation will expire on {{ Carbon\Carbon::parse($invitation->expires_at)->format('Y-m-d H:i') }}.

Thanks,<br>
{{ config('app.name') }}
@endcomponent
