import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Spinner } from "@/components/ui/spinner";
import { usePersonaStore } from "@/store/personaStore";
import { Persona } from "@/api/personaService";

interface PersonaFormData {
  name: string;
  background: string;
  interests: string;
  values: string;
  tone: string;
  expertise: string;
  purpose: string;
  is_active: boolean;
}

export function PersonaEdit() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { personas, fetchPersonas, updatePersona, isLoading, error } = usePersonaStore();
  const [persona, setPersona] = useState<Persona | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<PersonaFormData>({
    defaultValues: {
      name: "",
      background: "",
      interests: "",
      values: "",
      tone: "",
      expertise: "",
      purpose: "",
      is_active: true,
    },
  });

  useEffect(() => {
    fetchPersonas();
  }, [fetchPersonas]);

  useEffect(() => {
    if (personas.length > 0 && id) {
      const foundPersona = personas.find(p => p.id === parseInt(id));
      if (foundPersona) {
        setPersona(foundPersona);
        
        // Format arrays to comma-separated strings for the form
        form.reset({
          name: foundPersona.name || "",
          background: foundPersona.background || "",
          interests: foundPersona.interests ? foundPersona.interests.join(", ") : "",
          values: foundPersona.values ? foundPersona.values.join(", ") : "",
          tone: foundPersona.tone || "",
          expertise: foundPersona.expertise ? foundPersona.expertise.join(", ") : "",
          purpose: foundPersona.purpose || "",
          is_active: foundPersona.is_active !== undefined ? foundPersona.is_active : true,
        });
      }
    }
  }, [personas, id, form]);

  const onSubmit = async (data: PersonaFormData) => {
    if (!id) return;
    
    setIsSubmitting(true);
    try {
      // Convert comma-separated strings to arrays
      const formattedData = {
        ...data,
        interests: data.interests.split(",").map((item: string) => item.trim()).filter(Boolean),
        values: data.values.split(",").map((item: string) => item.trim()).filter(Boolean),
        expertise: data.expertise.split(",").map((item: string) => item.trim()).filter(Boolean),
      };

      await updatePersona(parseInt(id), formattedData);
      toast.success("Persona updated successfully");
      navigate(`/personas/${id}`);
    } catch (error) {
      toast.error("Failed to update persona");
      console.error("Error updating persona:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    navigate(`/personas/${id}`);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  if (error) {
    return <div className="text-red-500 text-center p-4">{error}</div>;
  }

  if (!persona) {
    return <div className="text-center p-4">Persona not found.</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Edit Persona</h1>
        <Button variant="outline" onClick={handleCancel}>
          Cancel
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Edit Persona</CardTitle>
          <CardDescription>Update the details of your virtual persona</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Enter persona name" {...field} disabled={isSubmitting} />
                    </FormControl>
                    <FormDescription>
                      The name of your virtual persona
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="background"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Background</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Enter persona background story"
                        className="min-h-[100px]"
                        {...field}
                        disabled={isSubmitting}
                      />
                    </FormControl>
                    <FormDescription>
                      A brief background story for your persona
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormField
                  control={form.control}
                  name="interests"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Interests</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Technology, Art, Science"
                          {...field}
                          disabled={isSubmitting}
                        />
                      </FormControl>
                      <FormDescription>
                        Comma-separated list of interests
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="values"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Values</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Honesty, Creativity, Innovation"
                          {...field}
                          disabled={isSubmitting}
                        />
                      </FormControl>
                      <FormDescription>
                        Comma-separated list of values
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormField
                  control={form.control}
                  name="tone"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Tone</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Professional, Casual, Humorous"
                          {...field}
                          disabled={isSubmitting}
                        />
                      </FormControl>
                      <FormDescription>
                        The tone of voice for this persona
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="expertise"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Expertise</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Marketing, Programming, Design"
                          {...field}
                          disabled={isSubmitting}
                        />
                      </FormControl>
                      <FormDescription>
                        Comma-separated list of expertise areas
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="purpose"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Purpose</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="The main purpose of this persona"
                        className="min-h-[100px]"
                        {...field}
                        disabled={isSubmitting}
                      />
                    </FormControl>
                    <FormDescription>
                      Describe the main purpose of this persona
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="is_active"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base">Active Status</FormLabel>
                      <FormDescription>
                        Set whether this persona is active or inactive
                      </FormDescription>
                    </div>
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                        disabled={isSubmitting}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />

              <div className="flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={handleCancel} disabled={isSubmitting}>
                  Cancel
                </Button>
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? <Spinner className="mr-2 h-4 w-4" /> : null}
                  Save Changes
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
