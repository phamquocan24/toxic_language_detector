<?php

namespace Modules\User\Http\Controllers\User;

use App\Http\Controllers\Controller;
use Modules\User\Entities\User;
use Modules\User\Entities\InvitationToken;
use Modules\User\Enums\UserRole;
use Modules\User\Mail\UserInvitation;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Facades\Hash;
use Carbon\Carbon;

class InvitationController extends Controller
{
    /**
     * Display the invitation form
     */
    public function showInviteForm()
    {
        $roles = [
            UserRole::ADMINISTRATOR => 'Admin',
            UserRole::MEMBER => 'Member'
        ];

        $pendingInvitations = InvitationToken::whereNull('accepted_at')
            ->orderBy('created_at', 'desc')
            ->get();

        return view('user::admin.users.invite', compact('roles', 'pendingInvitations'));
    }

    /**
     * Send an invitation to a new user
     */
    public function invite(Request $request)
    {
        $request->validate([
            'email' => 'required|email|unique:users,email',
            'role' => 'required|integer'
        ]);

        // Xóa token cũ nếu có
        InvitationToken::where('email', $request->email)->delete();

        // Tạo token mới
        $token = InvitationToken::create([
            'email' => $request->email,
            'role' => $request->role
        ]);

        // Gửi email
        try {
            Mail::to($request->email)->send(new UserInvitation($token));
            return redirect()->route('admin.users.invite')
                ->with('success', trans('user::users.messages.invitation_sent'));
        } catch (\Exception $e) {
            return redirect()->route('admin.users.invite')
                ->with('error', 'Error sending invitation: ' . $e->getMessage());
        }
    }

    /**
     * Resend an invitation
     */
    public function resend($id)
    {
        $invitation = InvitationToken::findOrFail($id);

        if ($invitation->isAccepted()) {
            return redirect()->back()
                ->with('error', trans('user::users.messages.invitation_already_accepted'));
        }

        // Cập nhật hạn token
        $invitation->expires_at = Carbon::now()->addDays(7);
        $invitation->save();

        // Gửi lại email
        try {
            Mail::to($invitation->email)->send(new UserInvitation($invitation));
            return redirect()->route('admin.users.invite')
                ->with('success', trans('user::users.messages.invitation_resent'));
        } catch (\Exception $e) {
            return redirect()->route('admin.users.invite')
                ->with('error', 'Error resending invitation: ' . $e->getMessage());
        }
    }

    /**
     * Show the invitation acceptance form
     */
    public function accept($token)
    {
        $invitation = InvitationToken::where('token', $token)->first();

        if (!$invitation) {
            return redirect()->route('login')
                ->with('error', trans('user::users.messages.invitation_invalid'));
        }

        if ($invitation->isExpired()) {
            return redirect()->route('login')
                ->with('error', trans('user::users.messages.invitation_expired'));
        }

        if ($invitation->isAccepted()) {
            return redirect()->route('login')
                ->with('info', trans('user::users.messages.invitation_already_accepted'));
        }

        return view('user::auth.accept_invitation', compact('invitation'));
    }

    /**
     * Register a new user from an invitation
     */
    public function register(Request $request)
    {
        $request->validate([
            'first_name' => 'required|string|max:255',
            'last_name' => 'required|string|max:255',
            'password' => 'required|string|min:8|confirmed',
            'token' => 'required'
        ]);

        $invitation = InvitationToken::where('token', $request->token)->first();

        if (!$invitation || $invitation->isExpired() || $invitation->isAccepted()) {
            return redirect()->route('login')
                ->with('error', trans('user::users.messages.invitation_invalid'));
        }

        // Tạo người dùng
        $user = User::create([
            'first_name' => $request->first_name,
            'last_name' => $request->last_name,
            'email' => $invitation->email,
            'password' => Hash::make($request->password),
            'role' => $invitation->role,
            'email_verified_at' => now()
        ]);

        // Đánh dấu token đã được chấp nhận
        $invitation->accepted_at = now();
        $invitation->save();

        // Auto login
        auth()->login($user);

        return redirect()->route('admin.dashboard.index')
            ->with('success', trans('user::users.messages.invitation_accepted'));
    }
}
