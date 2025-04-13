<?php declare(strict_types=1);

namespace Modules\User\Enums;

use BenSampo\Enum\Enum;

final class UserRole extends Enum
{
    const ADMINISTRATOR = 1;
    const MEMBER = 2;
}
