import { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { toast } from "sonner";
import { usePersonaStore } from "@/store/personaStore";
import { Persona } from "@/api/personaService";

export function PersonaDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { personas, fetchPersonas, isLoading, error } = usePersonaStore();
  const [persona, setPersona] = useState<Persona | null>(null);

  useEffect(() => {
    fetchPersonas();
  }, [fetchPersonas]);

  useEffect(() => {
    if (personas.length > 0 && id) {
      const foundPersona = personas.find(p => p.id === parseInt(id));
      setPersona(foundPersona || null);
    }
  }, [personas, id]);

  const handleEditClick = () => {
    navigate(`/personas/${id}/edit`);
  };

  const handleBackClick = () => {
    navigate("/personas");
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
        <h1 className="text-3xl font-bold">Persona Details</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleBackClick}>
            Back to List
          </Button>
          <Button onClick={handleEditClick}>
            Edit Persona
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <Avatar className="h-16 w-16">
              <AvatarImage src={persona.avatar_url || "/avatars/default.png"} alt={persona.name} />
              <AvatarFallback>{persona.name.substring(0, 2)}</AvatarFallback>
            </Avatar>
            <div>
              <CardTitle className="text-2xl">{persona.name}</CardTitle>
              <CardDescription>
                {persona.platform_connections?.length > 0
                  ? persona.platform_connections.map(p => p.platform_name).join(", ")
                  : "No platforms connected"}
              </CardDescription>
            </div>
            <Badge variant={persona.is_active ? "default" : "secondary"} className="ml-auto">
              {persona.is_active ? "Active" : "Inactive"}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <h3 className="text-lg font-medium mb-2">Background</h3>
            <p className="text-muted-foreground">{persona.background || "No background information provided."}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-medium mb-2">Interests</h3>
              <div className="flex flex-wrap gap-2">
                {persona.interests && persona.interests.length > 0 ? (
                  persona.interests.map((interest, index) => (
                    <Badge key={index} variant="outline">{interest}</Badge>
                  ))
                ) : (
                  <p className="text-muted-foreground">No interests specified.</p>
                )}
              </div>
            </div>

            <div>
              <h3 className="text-lg font-medium mb-2">Values</h3>
              <div className="flex flex-wrap gap-2">
                {persona.values && persona.values.length > 0 ? (
                  persona.values.map((value, index) => (
                    <Badge key={index} variant="outline">{value}</Badge>
                  ))
                ) : (
                  <p className="text-muted-foreground">No values specified.</p>
                )}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-medium mb-2">Tone</h3>
              <p className="text-muted-foreground">{persona.tone || "No tone specified."}</p>
            </div>

            <div>
              <h3 className="text-lg font-medium mb-2">Purpose</h3>
              <p className="text-muted-foreground">{persona.purpose || "No purpose specified."}</p>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-medium mb-2">Expertise</h3>
            <div className="flex flex-wrap gap-2">
              {persona.expertise && persona.expertise.length > 0 ? (
                persona.expertise.map((exp, index) => (
                  <Badge key={index} variant="outline">{exp}</Badge>
                ))
              ) : (
                <p className="text-muted-foreground">No expertise specified.</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6 pt-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">Content</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">{persona.content?.length || 0}</p>
                <p className="text-muted-foreground">Total content items</p>
              </CardContent>
              <CardFooter>
                <Button variant="outline" asChild className="w-full">
                  <Link to={`/content?personaId=${persona.id}`}>View Content</Link>
                </Button>
              </CardFooter>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">Interactions</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">{persona.interactions?.length || 0}</p>
                <p className="text-muted-foreground">Total interactions</p>
              </CardContent>
              <CardFooter>
                <Button variant="outline" asChild className="w-full">
                  <Link to={`/interactions?personaId=${persona.id}`}>View Interactions</Link>
                </Button>
              </CardFooter>
            </Card>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
