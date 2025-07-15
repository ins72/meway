<?php

namespace App\Yena\Pexels\Exceptions;

use Exception;
use App\Yena\Pexels\Photo;

class NoPexelsApiKeyProvided extends Exception
{
    public function __construct()
    {
        parent::__construct(
            'No API key provided. Please add PEXELS_API_KEY to your .env. To get a key visit: https://www.pexels.com/api/new/'
        );
    }
}
