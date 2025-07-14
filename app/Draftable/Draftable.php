<?php

namespace App\Draftable;


use App\User;
use Carbon\Carbon;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Collection;

class Draftable extends Model
{
    protected $table = 'draftables';

    protected $dates = ['created_at', 'updated_at', 'published_at'];

    protected $casts = ['draftable_data' => 'array', 'data' => 'array'];


    protected $fillable = ['draftable_id', 'draftable_data', 'draftable_model', 'published_at', 'user_id', 'data'];


    /**
     * Unpublished Drafts Scope
     * @param $query
     * @return mixed
     */
    public function ScopeUnPublished($query)
    {
        return $query->where('published_at', null);
    }

    /**
     * Published Drafts Scope
     * @param $query
     * @return mixed
     */
    public function ScopePublished($query)
    {
        return $query->where('published_at', '!=', null);
    }


    /**
     * Publish Method to publish the draft
     * @return $this
     * @throws \Exception
     */
    public function publish()
    {
        try {
            $new_class = $this->draftable_model::create($this->draftable_data);
            $this->published_at = Carbon::now();
            $this->draftable_id = $new_class->id;
            $this->save();
        } catch (\Exception $e) {
            throw new \Exception($e->getMessage());
        }
        return $this;
    }


    /**
     * Restore Method for old draft
     * @return $this
     * @throws \Exception
     */
    public function restore()
    {
        try {
            $new_class = $this->draftable_model::where('id', $this->draftable_id)->first();
            if (empty($new_class)) throw new \Exception('Cant Find Resource for ' . $this->draftable_model . ' with id ' . $this->draftable_id);
            $new_class->update($this->draftable_data);
            $this->published_at = Carbon::now();
            $this->draftable_id = $new_class->id;
            $this->save();
        } catch (\Exception $e) {
            throw new \Exception($e->getMessage());
        }
        return $this;
    }


    /**
     * Build the model for current draft
     * @return mixed
     * @throws \Exception
     */
    public function model()
    {
        try {
            $new_class = new $this->draftable_model();
            $new_class->forceFill($this->draftable_data);
            $new_class->published_at = $this->published_at;
        } catch (\Exception $e) {
            throw new \Exception($e->getMessage());
        }
        return $new_class;
    }


    /**
     * user relation
     * @return \Illuminate\Database\Eloquent\Relations\BelongsTo
     */
    public function user()
    {
        return $this->belongsTo(User::class, 'user_id');
    }


    /**
     * Set Additional data for the draft
     * @param $key
     * @param $value
     * @return $this
     */
    public function setData($key, $value)
    {
        $data = $this->data;
        $data[$key] = $value;
        $this->data = $data;
        $this->save();
        return $this;
    }


    /**
     * get data of draft
     */
    public function getData($key)
    {
        return isset($this->data[$key]) ? $this->data[$key] : null;
    }
}
