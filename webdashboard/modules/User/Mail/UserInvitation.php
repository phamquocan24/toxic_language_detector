<?php

namespace Modules\User\Mail;

use Modules\User\Entities\InvitationToken;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class UserInvitation extends Mailable
{
    use Queueable, SerializesModels;

    public $invitation;

    /**
     * Create a new message instance.
     */
    public function __construct(InvitationToken $invitation)
    {
        $this->invitation = $invitation;
    }

    /**
     * Get the message envelope.
     */
    public function envelope(): Envelope
    {
        // Bạn có thể giữ nguyên tiêu đề hoặc sử dụng hàm trans() nếu muốn đa ngôn ngữ
        return new Envelope(
            subject: 'Invitation to Join ' . config('app.name'),
            // Ví dụ sử dụng trans():
            // subject: trans('user::users.invitation_subject', ['app_name' => config('app.name')]),
        );
    }

    /**
     * Get the message content definition.
     */
    public function content(): Content
    {
        // *** Cập nhật đường dẫn markdown ở đây ***
        return new Content(
            // Sử dụng đường dẫn view trong module User
            markdown: 'user::admin.users.user_invitation',
        );
    }

    /**
     * Get the attachments for the message.
     *
     * @return array<int, \Illuminate\Mail\Mailables\Attachment>
     */
    public function attachments(): array
    {
        return [];
    }
}
